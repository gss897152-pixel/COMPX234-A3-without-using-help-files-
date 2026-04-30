import glob
import socket
import subprocess
import threading
import time

# Formatting request: Generate a protocol format with a length of 3 bits and operation instructions
def format_request(op, k, v=None):
    if op=="PUT": msg=f"{op} {k} {v}"
    else: msg=f"{op} {k}"
    return f"{len(msg):03} {msg}"

# The child process starts the server without blocking the client's operation
def start_server():
    subprocess.Popen(['python','server.py'])

# Read the file and send a request to the server
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

# Client main function
def main():

    threading.Thread(target=start_server,daemon=True).start()
    time.sleep(1)

    for fn in glob.glob('client_*.txt'):
        print(f"Processing {fn}")
        send_file('localhost',51234,fn)
    time.sleep(5)

if __name__ == '__main__':
    main()