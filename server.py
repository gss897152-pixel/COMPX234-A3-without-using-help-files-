import socket
import threading

class TupleSpace:
    def __init__(self):
        self.tuple_space = {}

    def put(self, key, value):
        if key in self.tuple_space:
            return "024 ERR key already exists"
        self.tuple_space[key] = value
        return f"0{len(key)+len(value)+14} OK ({key},{value}) added"

    def get(self, key):
        if key not in self.tuple_space:
            return "024 ERR key does not exist"
        val = self.tuple_space.pop(key)
        return f"0{len(key)+len(val)+16} OK ({key},{val}) removed"

    def read(self, key):
        if key not in self.tuple_space:
            return "024 ERR key does not exist"
        val = self.tuple_space[key]
        return f"0{len(key)+len(val)+14} OK ({key},{val}) read"

def start_server():
    host = 'localhost'
    port = 51234
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}")

if __name__ == '__main__':
    start_server()