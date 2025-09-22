 # server.py - Server code

import socket
import os
import subprocess
import threading
import time
import sys
import ollama

HOST = '0.0.0.0'
PORT = 65432
BUFFER_SIZE = 4096

def get_current_path():
    return os.getcwd()

def execute_command(command):
    try:
        if command.startswith('cd '):
            path = command[3:].strip()
            if not path:
                return "Error: No path provided"
            try:
                os.chdir(path)
                return f"Directory changed to: {get_current_path()}"
            except Exception as e:
                return f"Error changing directory: {str(e)}"

        # Execute normal command
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output, error = process.communicate()
        result = output + error
        return result.decode('utf-8', errors='ignore')

    except Exception as e:
        return f"Error executing command: {str(e)}"

def send_file(conn, file_path):
    """Send file to client"""
    try:
        if not os.path.exists(file_path):
            conn.sendall(b'FileNotFound')
            return False

        file_size = os.path.getsize(file_path)
        conn.sendall(str(file_size).encode())

        # Wait for ACK
        if conn.recv(3) != b'ACK':
            return False

        # Send file
        sent_bytes = 0
        with open(file_path, 'rb') as f:
            while sent_bytes < file_size:
                chunk = f.read(BUFFER_SIZE)
                conn.sendall(chunk)
                sent_bytes += len(chunk)
        return True
    except Exception as e:
        print(f"File send error: {e}")
        return False

def recv_file(conn, save_path):
    """Receive file from client"""
    try:
        file_size = int(conn.recv(1024).decode())
        conn.sendall(b'ACK')

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        received_bytes = 0
        with open(save_path, 'wb') as f:
            while received_bytes < file_size:
                chunk = conn.recv(BUFFER_SIZE)
                if not chunk:
                    break
                f.write(chunk)
                received_bytes += len(chunk)
        return True
    except Exception as e:
        print(f"File receive error: {e}")
        return False

def handle_client(conn, addr):
    print(f'New connection: {addr}')
    try:
        while True:
            current_path = get_current_path()
            conn.sendall(f"PATH:{current_path}".encode())

            data = conn.recv(10240).decode()
            if not data:
                break

            if data.startswith('OLLAMA:'):
                try:
                    _, model_name, prompt = data.split(':', 2)
                    response = ollama.generate(model=model_name, prompt=prompt)
                    conn.sendall(response['response'].encode())
                except Exception as e:
                    conn.sendall(f"Ollama error: {str(e)}".encode())

            elif data.startswith('DOWNLOAD:'):
                try:
                    file_name = data.split(':', 1)[1].strip()
                    if not file_name:
                        conn.sendall(b'FileNameError')
                        continue

                    file_path = os.path.join(get_current_path(), file_name)

                    if not os.path.isfile(file_path):
                        conn.sendall(b'FileNotFound')
                        continue

                    if send_file(conn, file_path):
                        conn.sendall(b'FileSent')
                    else:
                        conn.sendall(b'FileError')
                except Exception as e:
                    print(f"Download error: {e}")
                    conn.sendall(b'DownloadError')

            elif data.startswith('UPLOAD:'):
                file_info = data.split(':', 1)[1]
                file_name, save_path = file_info.split('<SEP>')
                full_path = os.path.join(save_path, file_name)
                if recv_file(conn, full_path):
                    conn.sendall(b'FileUploaded')
                else:
                    conn.sendall(b'UploadError')

            else:
                result = execute_command(data)
                conn.sendall(result.encode())

    except (ConnectionResetError, BrokenPipeError):
        print(f"Connection lost: {addr}")
    except Exception as e:
        print(f"General error: {e}")
    finally:
        conn.close()
        print(f"Connection closed: {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Server running on port {PORT}...")

        while True:
            try:
                conn, addr = s.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                thread.start()
                print(f"New connection ({threading.active_count()} active clients)")
            except Exception as e:
                print(f"Connection accept error: {e}")

if __name__ == "__main__":
    main()