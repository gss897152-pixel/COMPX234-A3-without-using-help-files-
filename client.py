import socket
import subprocess
import threading
import time

def format_request(op, k, v=None):
    if op=="PUT": msg=f"{op} {k} {v}"
    else: msg=f"{op} {k}"
    return f"{len(msg):03} {msg}"

def start_server():
    subprocess.Popen(['python','server.py'])

def send_file(host,port,fn):
    s=socket.socket()
    s.connect((host,port))
    with open(fn) as f:
        for line in f:
            line=line.strip()
            if not line:continue
            parts=line.split(maxsplit=2)
            if len(parts)<2:
                print(f"Invalid: {line}")
                continue
            op,k=parts[0],parts[1]
            v=parts[2] if len(parts)>2 else None
            req=format_request(op,k,v)
            s.send(req.encode())
            res=s.recv(1024).decode()
            print(f"Sent: {line} → {res}")
    s.close()

def main():
    threading.Thread(target=start_server,daemon=True).start()
    time.sleep(1)
    send_file('localhost',51234,'client_test1.txt')

if __name__ == '__main__':
    main()