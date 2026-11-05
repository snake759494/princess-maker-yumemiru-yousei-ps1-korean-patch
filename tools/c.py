import socket,sys,time
for i in range(120):
    try: s=socket.create_connection(('127.0.0.1',2399));break
    except OSError: time.sleep(1)
s.sendall(' '.join(sys.argv[1:]).encode())
r=b''
while True:
    d=s.recv(65536)
    if not d: break
    r+=d
print(r.decode())
