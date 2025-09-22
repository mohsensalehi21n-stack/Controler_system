# client.py - Client code

import socket
import os
import threading
import sys
import time

SERVER_IP = '192.168.52.1'  # Replace with your server IP
PORT = 65432
BUFFER_SIZE = 4096

current_path = "Unknown"

def send_file(s, file_path, save_path):
    try:
        if not os.path.exists(file_path):
            print("File does not exist!")
            return False

        file_name = os.path.basename(file_path)
        s.sendall(f"UPLOAD:{file_name}<SEP>{save_path}".encode())

        if s.recv(1024) != b'ACK':
            return False

        file_size = os.path.getsize(file_path)
        s.sendall(str(file_size).encode())

        if s.recv(3) != b'ACK':
            return False

        sent_bytes = 0
        with open(file_path, 'rb') as f:
            while sent_bytes < file_size:
                chunk = f.read(BUFFER_SIZE)
                s.sendall(chunk)
                sent_bytes += len(chunk)
        print(s.recv(1024).decode())
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False

def recv_file(s, save_path):
    try:
        file_size = int(s.recv(1024).decode())
        s.sendall(b'ACK')

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        received_bytes = 0

        with open(save_path, 'wb') as f:
            while received_bytes < file_size:
                chunk = s.recv(BUFFER_SIZE)
                f.write(chunk)
                received_bytes += len(chunk)
        print("File received successfully!")
        return True
    except Exception as e:
        print(f"Receive error: {e}")
        return False

def listen_for_path(s):
    global current_path
    while True:
        try:
            data = s.recv(10240)
            if data.startswith(b'PATH:'):
                current_path = data[5:].decode()
        except:
            break

def main():
    global current_path
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, PORT))
            print("Connected to server!")

            path_thread = threading.Thread(target=listen_for_path, args=(s,), daemon=True)
            path_thread.start()

            while True:
                try:
                    cmd = input(f"{current_path}> ")

                    if cmd.lower() == 'exit':
                        break

                    if cmd.startswith('upload '):
                        parts = cmd.split(' ', 2)
                        if len(parts) == 3:
                            send_file(s, parts[1], parts[2])
                        else:
                            print("Format: upload [local_file] [server_path]")

                    elif cmd.startswith('download '):
                        parts = cmd.split(' ', 1)
                        if len(parts) == 2:
                            s.sendall(f"DOWNLOAD:{parts[1]}".encode())
                            recv_file(s, os.path.basename(parts[1]))
                        else:
                            print("Format: download [server_file_path]")

                    elif cmd.startswith('ollama '):
                        parts = cmd.split(' ', 2)
                        if len(parts) == 3:
                            s.sendall(f"OLLAMA:{parts[1]}:{parts[2]}".encode())
                            response = s.recv(65536).decode('utf-8', 'ignore')
                            print("\nModel response:")
                            print(response)
                        else:
                            print("Format: ollama [model_name] [prompt]")

                    else:
                        s.sendall(cmd.encode())
                        response = s.recv(65536).decode('utf-8', 'ignore')
                        print(response)

                except (ConnectionResetError, BrokenPipeError):
                    print("Connection lost! Retrying...")
                    break
                except Exception as e:
                    print(f"Error: {e}")

            s.close()
            print("Connection closed")
        except ConnectionRefusedError:
            print("Server unavailable")
