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

def client_thread(host, port, client_id, semaphore):
    # Thread function for a single concurrent test client.
    with semaphore:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(f"Client {client_id} connected")

            # Test requests (covers success + error scenarios)
            requests = [
                f"PUT shared-key test-value-{client_id}",  # Shared key for race condition test
                f"READ shared-key",
                f"PUT unique-key-{client_id} value-{client_id}",
                f"GET unique-key-{client_id}",
                f"READ unique-key-{client_id}",  # Expected error
                f"GET non-existent-key"  # Expected error
            ]

            for idx, request in enumerate(requests):
                time.sleep(0.01)  # Small delay to simulate real network
                formatted_request = format_request(*request.split(maxsplit=2))
                client_socket.send(formatted_request.encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                print(f"Client {client_id} [{idx+1}]: Sent={formatted_request}, Received={response}")

            client_socket.close()
            print(f"Client {client_id} disconnected")
        except Exception as e:
            print(f"Client {client_id} error: {e}")

def test_concurrent_access():
    # Simulate concurrent clients to test thread safety and race conditions.
    host = 'localhost'
    port = 51234
    max_concurrent = 5
    total_clients = 10
    semaphore = threading.Semaphore(max_concurrent)
    threads = []

    print(f"Starting concurrent test: {total_clients} clients (max {max_concurrent} concurrent)")
    for client_id in range(total_clients):
        thread = threading.Thread(target=client_thread, args=(host, port, client_id, semaphore))
        thread.start()
        threads.append(thread)
        time.sleep(0.05)  # Stagger thread starts to avoid thundering herd

    for thread in threads:
        thread.join()

    # Print test summary
    print("\n=== Concurrent Test Complete ===")
    print(f"Total clients: {total_clients}")
    print(f"Max concurrent: {max_concurrent}")
    print(f"Requests per client: 6")

if __name__ == '__main__':
    print("Waiting for server to initialize...")
    time.sleep(10)
    test_concurrent_access()