import socket
import ipaddress

##TODO: implement UDP message authentication and data extract

hostmask = str(ipaddress.ip_network(socket.gethostbyname(socket.gethostname())).hostmask)

port = 13117

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((hostmask, port))
    data, addr = listener.recvfrom(1024)
    print(addr)
    print(data)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(addr)