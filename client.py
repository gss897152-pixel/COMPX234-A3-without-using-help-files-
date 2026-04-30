import socket

def format_request(op, k, v=None):
    if op=="PUT": msg=f"{op} {k} {v}"
    else: msg=f"{op} {k}"
    return f"{len(msg):03} {msg}"

def main():
    s=socket.socket()
    s.connect(('localhost',51234))
    req=format_request("PUT","test","123")
    s.send(req.encode())
    print(s.recv(1024).decode())
    s.close()

if __name__ == '__main__':
    main()