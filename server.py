import socket
import threading
import time

class TupleSpace:
    def __init__(self):
        self.tuple_space = {}
        self.lock = threading.Lock()
    def put(self, key, value):
        with self.lock:
            if key in self.tuple_space: return "024 ERR key already exists"
            self.tuple_space[key] = value
            return f"0{len(key)+len(value)+14} OK ({key},{value}) added"
    def get(self, key):
        with self.lock:
            if key not in self.tuple_space: return "024 ERR key does not exist"
            val = self.tuple_space.pop(key)
            return f"0{len(key)+len(val)+16} OK ({key},{val}) removed"
    def read(self, key):
        with self.lock:
            if key not in self.tuple_space: return "024 ERR key does not exist"
            val = self.tuple_space[key]
            return f"0{len(key)+len(val)+14} OK ({key},{val}) read"

class ServerStatistics:
    def __init__(self):
        self.total_clients=self.total_operations=self.total_reads=self.total_gets=self.total_puts=self.errors=0
    def increment_clients(self): self.total_clients+=1
    def increment_operations(self): self.total_operations+=1
    def increment_reads(self): self.total_reads+=1
    def increment_gets(self): self.total_gets+=1
    def increment_puts(self): self.total_puts+=1
    def increment_errors(self): self.errors+=1

def handle_client(conn, addr, ts, stats):
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data: break
            conn.send(b"024 OK test")
    except: pass
    finally: conn.close()

def start_server():
    host, port = 'localhost',51234
    s = socket.socket()
    s.bind((host,port))
    s.listen(5)
    ts = TupleSpace()
    stats = ServerStatistics()
    while True:
        conn,addr = s.accept()
        stats.increment_clients()
        threading.Thread(target=handle_client, args=(conn,addr,ts,stats)).start()

if __name__ == '__main__':
    start_server()