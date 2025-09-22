import socket
import os
import threading

HOST = '0.0.0.0'
PORT = 65432
BUFFER_SIZE = 4096

def get_current_path():
    return os.getcwd()

def send_file(conn, file_path):
    """Send file to client with progress support"""
    try:
        if not os.path.exists(file_path):
            conn.sendall(b'FileNotFound')
            return False
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        conn.sendall(f"{file_name}<SEP>{file_size}".encode())
        
        if conn.recv(3) != b'ACK':
            return False
        
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

def handle_client(conn, addr):
    print(f"New connection from {addr}")
    try:
        while True:
            # Send current working directory to client
            conn.sendall(f"PATH:{get_current_path()}".encode())
            
            # Receive command from client
            data = conn.recv(1024).decode()
            if not data:
                break

            if data.startswith('DOWNLOAD:'):
                file_path = data.split(':', 1)[1].strip()
                full_path = os.path.join(get_current_path(), file_path)
                
                if not os.path.exists(full_path):
                    conn.sendall(b'FileNotFound')
                    continue
                
                if send_file(conn, full_path):
                    conn.sendall(b'DownloadComplete')
                else:
                    conn.sendall(b'DownloadError')
    except Exception as e:
        print(f"Client communication error: {e}")
    finally:
        conn.close()
        print(f"Connection with {addr} closed")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server running on port {PORT}...")

        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    main()
