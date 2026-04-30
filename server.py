import socket
import threading
import time

# TupleSpace class to manage tuple space
class TupleSpace:
    def __init__(self):
        # Store key - value pairs
        self.tuple_space = {}
        # Thread - safe lock
        self.lock = threading.Lock()

    # Add a tuple to the space
    def put(self, key, value):
        with self.lock:
            if key in self.tuple_space:
                return "024 ERR key already exists"
            if len(key) > 999 or len(value) > 999 or len(key) + len(value) > 970:
                return "024 ERR key or value too long"
            self.tuple_space[key] = value
            return f"0{len(key) + len(value) + 14} OK ({key}, {value}) added"

    # Get and remove a tuple
    def get(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            value = self.tuple_space.pop(key)
            return f"0{len(key) + len(value) + 16} OK ({key}, {value}) removed"

    # Read a tuple without removal
    def read(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            value = self.tuple_space[key]
            return f"0{len(key) + len(value) + 14} OK ({key}, {value}) read"

# ServerStatistics class to track server stats
class ServerStatistics:
    def __init__(self):
        self.total_clients = 0
        self.total_operations = 0
        self.total_reads = 0
        self.total_gets = 0
        self.total_puts = 0
        self.errors = 0

    def increment_clients(self):
        self.total_clients += 1

    def increment_operations(self):
        self.total_operations += 1

    def increment_reads(self):
        self.total_reads += 1

    def increment_gets(self):
        self.total_gets += 1

    def increment_puts(self):
        self.total_puts += 1

    def increment_errors(self):
        self.errors += 1

def start_server():
    host = 'localhost'
    port = 51234
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}")
    # Create TupleSpace and ServerStatistics instances
    tuple_space = TupleSpace()
    stats = ServerStatistics()

    def print_summary_periodically():
        while True:
            print_server_summary(tuple_space, stats)
            time.sleep(10)

    # Start summary thread
    summary_thread = threading.Thread(target=print_summary_periodically)
    summary_thread.daemon = True
    summary_thread.start()

    try:
        while True:
            client_conn, client_addr = server_socket.accept()
            stats.increment_clients()
            print(f"Accepted connection from {client_addr}")
            # Start client - handling thread
            client_handler = threading.Thread(target=handle_client, args=(client_conn, client_addr, tuple_space, stats))
            client_handler.start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        server_socket.close()

def handle_client(client_conn, client_addr, tuple_space, stats):
    # Handle client requests in a separate thread
    try:
        while True:
            data = client_conn.recv(1024).decode('utf-8')
            if not data:
                break

            # Parse the request
            length = int(data[:3])
            request = data[4:length+4]
            parts = request.split(maxsplit=2)
            if len(parts) < 2:
                response = "024 ERR invalid request"
                stats.increment_errors()
                client_conn.send(response.encode('utf-8'))
                continue

            operation = parts[0]
            key = parts[1]
            value = parts[2] if len(parts) > 2 else None

            # Process the request based on the operation
            if operation == 'GET':
                stats.increment_operations()
                stats.increment_gets()
                response = tuple_space.get(key)
                if "ERR" in response:
                    stats.increment_errors()
            elif operation == 'PUT':
                stats.increment_operations()
                stats.increment_puts()
                response = tuple_space.put(key, value)
                if "ERR" in response:
                    stats.increment_errors()
            elif operation == 'READ':
                stats.increment_operations()
                stats.increment_reads()
                response = tuple_space.read(key)
                if "ERR" in response:
                    stats.increment_errors()
            else:
                response = "024 ERR invalid operation"
                stats.increment_errors()

            client_conn.send(response.encode('utf-8'))

    except Exception as e:
        print(f"Error handling client {client_addr}: {e}")
        stats.increment_errors()
    finally:
        client_conn.close()

def print_server_summary(tuple_space, stats):
    # Print a summary of the server's current state
    num_tuples = len(tuple_space.tuple_space)
    if num_tuples == 0:
        avg_tuple_size = avg_key_size = avg_value_size = 0
    else:
        total_tuple_size = sum(len(key) + len(value) for key, value in tuple_space.tuple_space.items())
        avg_tuple_size = total_tuple_size / num_tuples
        avg_key_size = sum(len(key) for key in tuple_space.tuple_space.keys()) / num_tuples
        avg_value_size = sum(len(value) for value in tuple_space.tuple_space.values()) / num_tuples

    print(f"Current tuple space size: {num_tuples}")
    print(f"Average tuple size: {avg_tuple_size:.2f} bytes")
    print(f"Average key size: {avg_key_size:.2f} bytes")
    print(f"Average value size: {avg_value_size:.2f} bytes")
    print(f"Total clients connected: {stats.total_clients}")
    print(f"Total operations: {stats.total_operations}, READs: {stats.total_reads}, GETs: {stats.total_gets}, PUTs: {stats.total_puts}")
    print(f"Total errors: {stats.errors}")

if __name__ == '__main__':
    start_server()