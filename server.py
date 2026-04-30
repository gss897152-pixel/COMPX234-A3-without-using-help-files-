import socket
import threading
import time

class TupleSpace:
    def __init__(self):
        self.tuple_space = {}
        self.lock = threading.Lock()
    def put(self, key, value):
        with self.lock:
            if key in self.tuple_space:
                return "024 ERR key already exists"
            if len(key)+len(value)>970 or len(key)>999 or len(value)>999:
                return "024 ERR key or value too long"
            self.tuple_space[key] = value
            return f"0{len(key)+len(value)+14} OK ({key}, {value}) added"
    def get(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            val = self.tuple_space.pop(key)
            return f"0{len(key)+len(val)+16} OK ({key}, {val}) removed"
    def read(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            val = self.tuple_space[key]
            return f"0{len(key)+len(val)+14} OK ({key}, {val}) read"

class ServerStatistics:
    def __init__(self):
        self.total_clients=0
        self.total_operations=0
        self.total_reads=0
        self.total_gets=0
        self.total_puts=0
        self.errors=0
    def increment_clients(self): self.total_clients+=1
    def increment_operations(self): self.total_operations+=1
    def increment_reads(self): self.total_reads+=1
    def increment_gets(self): self.total_gets+=1
    def increment_puts(self): self.total_puts+=1
    def increment_errors(self): self.errors+=1

def print_server_summary(ts, stats):
    n=len(ts.tuple_space)
    print(f"Tuples: {n}, Clients: {stats.total_clients}, Errors: {stats.errors}")

def handle_client(conn, addr, ts, stats):
    try:
        while True:
            data=conn.recv(1024).decode()
            if not data:break
            l=int(data[:3])
            req=data[4:l+4]
            parts=req.split(maxsplit=2)
            if len(parts)<2:
                stats.increment_errors()
                conn.send(b"024 ERR invalid request")
                continue
            op,k=parts[0],parts[1]
            v=parts[2] if len(parts)>2 else None
            stats.increment_operations()
            if op=="PUT":
                stats.increment_puts()
                res=ts.put(k,v)
            elif op=="GET":
                stats.increment_gets()
                res=ts.get(k)
            elif op=="READ":
                stats.increment_reads()
                res=ts.read(k)
            else:
                stats.increment_errors()
                res="024 ERR invalid operation"
            if "ERR" in res: stats.increment_errors()
            conn.send(res.encode())
    except: stats.increment_errors()
    finally: conn.close()

def start_server():
    host,port='localhost',51234
    s=socket.socket()
    s.bind((host,port))
    s.listen(5)
    ts=TupleSpace()
    stats=ServerStatistics()
    def loop():
        while True:
            print_server_summary(ts,stats)
            time.sleep(10)
    threading.Thread(target=loop,daemon=True).start()
    while True:
        conn,addr=s.accept()
        stats.increment_clients()
        threading.Thread(target=handle_client,args=(conn,addr,ts,stats)).start()

if __name__ == '__main__':
    start_server()