import socket
import os
import sys
import time

SERVER_IP = '192.168.142.1'  # Replace with your server IP
PORT = 65432
BUFFER_SIZE = 4096

def draw_progress_bar(percent):
    """Display progress bar in terminal"""
    bar_length = 30
    filled = int(bar_length * percent / 100)
    bar = '█' * filled + '-' * (bar_length - filled)
    sys.stdout.write(f'\r[{bar}] {percent:.1f}%')
    sys.stdout.flush()
    if percent >= 100:
        print()

def download_file(s, remote_path):
    """Download file with progress display"""
    try:
        # Send download request
        s.sendall(f"DOWNLOAD:{remote_path}".encode())
        
        # Receive file info
        file_info = s.recv(1024).decode()
        if file_info == "FileNotFound":
            print("\n✗ File not found on server!")
            return False
        
        file_name, file_size = file_info.split('<SEP>')
        file_size = int(file_size)
        
        # Send ACK to confirm readiness
        s.sendall(b'ACK')
        
        # Receive file
        received = 0
        start_time = time.time()
        
        with open(file_name, 'wb') as f:
            while received < file_size:
                chunk = s.recv(min(BUFFER_SIZE, file_size - received))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                percent = (received / file_size) * 100
                draw_progress_bar(percent)
        
        # Check result
        result = s.recv(1024)
        if result == b'DownloadComplete':
            speed = received / (1024 * (time.time() - start_time))
            print(f"\n✓ Download completed! (Speed: {speed:.2f} KB/s)")
            return True
        else:
            print("\n✗ Download error!")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

def process_command(cmd):
    """Smart input command processing"""
    cmd = cmd.strip().lower()
    
    # Exit commands
    if cmd in ['exit', 'quit', 'q']:
        return 'exit'
    
    # Download commands
    download_prefixes = ['download', 'dl', 'get', 'd:']
    for prefix in download_prefixes:
        if cmd.startswith(prefix):
            separator = ':' if ':' in prefix else ' '
            parts = cmd.split(separator, 1)
            if len(parts) > 1:
                return ('download', parts[1].strip())
    
    return None

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((SERVER_IP, PORT))
        print("✓ Connected to server")
        print("Available commands:")
        print("- download <filename> or d:<filename>")
        print("- exit to quit")
        
        while True:
            cmd = input("\nCommand> ").strip()
            processed = process_command(cmd)
            
            if not processed:
                print("Invalid command! Please use one of the following formats:")
                print("download <filename>")
                print("d:<filename>")
                print("exit")
                continue
                
            if processed == 'exit':
                break
                
            if processed[0] == 'download':
                print(f"Downloading {processed[1]}...")
                download_file(s, processed[1])
                
    except ConnectionRefusedError:
        print("✗ Server is unavailable!")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    finally:
        s.close()
        print("Connection closed")

if __name__ == "__main__":
    main()
