import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 51234))
    print("Client connected to server")
    client_socket.close()

if __name__ == '__main__':
    main()