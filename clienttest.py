import threading
import socket
import time

def format_request(op,k,v=None):
    if op=="PUT":msg=f"{op} {k} {v}"
    else:msg=f"{op} {k}"
    return f"{len(msg):03} {msg}"

def client(host,port,reqs,sem):
    with sem:
        s=socket.socket()
        s.connect((host,port))
        for r in reqs:
            fr=format_request(*r.split(maxsplit=2))
            s.send(fr.encode())
            res=s.recv(1024).decode()
            print(f"{fr} → {res}")
        s.close()

def test():
    host,port='localhost',51234
    reqs=["PUT key1 val1","GET key1","READ key2","PUT key2 val2","GET key2"]
    sem=threading.Semaphore(5)
    ts=[]
    for _ in range(10):
        t=threading.Thread(target=client,args=(host,port,reqs,sem))
        t.start()
        ts.append(t)
    for t in ts:t.join()

if __name__ == '__main__':
    time.sleep(10)
    test()