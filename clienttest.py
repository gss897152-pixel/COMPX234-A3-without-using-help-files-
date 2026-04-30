import threading
import socket
import time

def format_request(op,k,v=None):
    if op=="PUT":msg=f"{op} {k} {v}"
    else:msg=f"{op} {k}"
    return f"{len(msg):03} {msg}"

def client(host,port,reqs):
    s=socket.socket()
    s.connect((host,port))
    for r in reqs:
        s.send(format_request(*r.split()).encode())
        print(s.recv(1024).decode())
    s.close()

def test():
    reqs=["PUT k1 v1","GET k1","READ k2"]
    for _ in range(5):
        threading.Thread(target=client,args=('localhost',51234,reqs)).start()

if __name__ == '__main__':
    time.sleep(5)
    test()