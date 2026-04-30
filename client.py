import glob
import os
import socket
import threading
import time
import subprocess

def format_request(operation, key, value=None):
    # Format request message with 3-digit length prefix per assignment protocol.
    if operation == 'PUT':
        request = f"{operation} {key} {value}"
    else:
        request = f"{operation} {key}"
    return f"{len(request):03} {request}"

def send_request_to_server(host, port, filename):
    # Connect to server, send requests line-by-line, and print synchronous responses.
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(maxsplit=2)
            if len(parts) < 2:
                print(f"Invalid request format: {line}")
                continue

            operation = parts[0]
            key = parts[1]
            value = parts[2] if len(parts) > 2 else None

            # Format the request message
            request = format_request(operation, key, value)
            client_socket.send(request.encode('utf-8'))

            # Wait for the response
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Sent: {line}, Received: {response}")

    client_socket.close()

def main():
    # Main client entry: start server subprocess and process all client_*.txt files.
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    time.sleep(1)

    client_files = glob.glob('client_*.txt')
    for file in client_files:
        print(f"Processing {file}")
        send_request_to_server('localhost', 51234, file)

    time.sleep(5)

def start_server():
    # Start the server in a separate process.
    subprocess.Popen(['python', 'server.py'])

if __name__ == '__main__':
    main()