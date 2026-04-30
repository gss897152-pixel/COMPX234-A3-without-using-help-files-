import threading
import socket
import time

def format_request(operation, key, value=None):
    # Format the request message according to the protocol.
    if operation == 'PUT':
        request = f"{operation} {key} {value}"
    else:
        request = f"{operation} {key}"
    return f"{len(request):03} {request}"

def client_thread(host, port, requests, semaphore):
    # Function for each client thread to send requests and receive responses
    with semaphore:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))

            for request in requests:
                formatted_request = format_request(*request.split(maxsplit=2))
                client_socket.send(formatted_request.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Sent: {formatted_request}, Received: {response}")

            client_socket.close()
        except Exception as e:
            print(f"Client thread encountered an error: {e}")

def test_concurrent_access():
    # Function to simulate multiple clients accessing the server concurrently
    host = 'localhost'
    port = 51234
    requests = [
        "PUT key1 value1",
        "GET key1",
        "READ key2",
        "PUT key2 value2",
        "GET key2"
    ]

    # Limit the number of clients running at the same time
    max_clients = 5
    semaphore = threading.Semaphore(max_clients)

    threads = []
    # Simulate 10 client threads
    for _ in range(10):
        thread = threading.Thread(target=client_thread, args=(host, port, requests, semaphore))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    # Wait to ensure the server is fully started
    time.sleep(10)
    test_concurrent_access()