import socket
import threading
import time

# Tuple space class: Responsible for storing key-value pairs and ensuring thread safety
class TupleSpace:
    def __init__(self):
        self.tuple_space = {}  
        self.lock = threading.Lock()  

    # Store key-value pairs. If they already exist, an error will be reported
    def put(self, key, value):
        with self.lock:
            if key in self.tuple_space:
                return "024 ERR key already exists"

            if len(key) > 999 or len(value) > 999 or len(key) + len(value) > 970:
                return "024 ERR key or value too long"
            self.tuple_space[key] = value
            return f"0{len(key)+len(value)+14} OK ({key},{value}) added"

    # Get and delete key-value pairs
    def get(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            val = self.tuple_space.pop(key)
            return f"0{len(key)+len(val)+16} OK ({key},{val}) removed"

    # Read key-value pairs without deleting them
    def read(self, key):
        with self.lock:
            if key not in self.tuple_space:
                return "024 ERR key does not exist"
            val = self.tuple_space[key]
            return f"0{len(key)+len(val)+14} OK ({key},{val}) read"

# Server-side statistics category: Records the number of clients, operations, and errors
class ServerStatistics:
    def __init__(self):
        self.total_clients = 0
        self.total_operations = 0
        self.total_reads = 0
        self.total_gets = 0
        self.total_puts = 0
        self.errors = 0

    # The statistical count increases automatically
    def increment_clients(self): self.total_clients +=1
    def increment_operations(self): self.total_operations +=1
    def increment_reads(self): self.total_reads +=1
    def increment_gets(self): self.total_gets +=1
    def increment_puts(self): self.total_puts +=1
    def increment_errors(self): self.errors +=1

# Print the server statistics information at regular intervals
def print_summary(ts, stats):
    n = len(ts.tuple_space)
    print(f"Tuples: {n}, Clients: {stats.total_clients}, Ops: {stats.total_operations}")

# Handle a single client request (independent thread
def handle_client(conn, addr, ts, stats):
    try:
        while True:
            data = conn.recv(1024).decode()
            if not data: break
            # Parsing protocol: The first three digits represent the length
            length=int(data[:3])
            req=data[4:length+4]
            parts=req.split(maxsplit=2)
            if len(parts)<2:
                stats.increment_errors()
                conn.send(b"024 ERR invalid")
                continue
            op,k=parts[0],parts[1]
            v=parts[2] if len(parts)>2 else None
            stats.increment_operations()
            # Execute the corresponding logic based on the operation type
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
                res="024 ERR invalid op"
            if "ERR" in res: stats.increment_errors()
            conn.send(res.encode())
    except: stats.increment_errors()
    finally: conn.close()

# Start the main function of the server
def start_server():
    host,port='localhost',51234
    s=socket.socket()
    s.bind((host,port))
    s.listen(5)
    ts=TupleSpace()
    stats=ServerStatistics()
    # Enable an independent thread to print statistics at regular intervals
    def loop_print():
        while True:
            print_summary(ts,stats)
            time.sleep(10)
    threading.Thread(target=loop_print,daemon=True).start()
    # Enable an independent thread to print statistics at regular intervals
    while True:
        conn,addr=s.accept()
        stats.increment_clients()
        threading.Thread(target=handle_client, args=(conn,addr,ts,stats)).start()

if __name__ == '__main__':
    start_server()