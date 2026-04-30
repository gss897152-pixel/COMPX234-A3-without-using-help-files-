import socket

def format_request(op, k, v=None):
    if op=="PUT": msg=f"{op} {k} {v}"
    else: msg=f"{op} {k}"
    return f"{len(msg):03} {msg}"

def send_file(host,port,fn):
    s=socket.socket()
    s.connect((host,port))
    with open(fn) as f:
        for line in f:
            line=line.strip()
            if not line:continue
            parts=line.split(maxsplit=2)
            op,k=parts[0],parts[1]
            v=parts[2] if len(parts)>2 else None
            req=format_request(op,k,v)
            s.send(req.encode())
            print(s.recv(1024).decode())
    s.close()

def main():
    send_file('localhost',51234,'client_test1.txt')

if __name__ == '__main__':
    main()