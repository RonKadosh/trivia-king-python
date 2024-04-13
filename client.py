import socket
import ipaddress
import struct

class Client:
    def __init__(self):
        self._hostmask = str(ipaddress.ip_network(socket.gethostbyname(socket.gethostname())).hostmask)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def listen_to_udp_messages(self):
        print("Client started, listening for offer requests...")
        udp_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_listener.bind((self._hostmask, 13117))
        data, addr = udp_listener.recvfrom(1024)
        print("UDP broadcast recieved: " + str(data) + " from: " + str(addr))
        unpack_format = '>Ih32sH'
        magic_cookie, offer, server_name, port = struct.unpack(unpack_format, data)
        udp_listener.close()
        self._sock.connect((addr[0], port))
        self._sock.send(b'NAME')
    

##TODO: implement UDP message authentication and data extract

#hostmask = str(ipaddress.ip_network(socket.gethostbyname(socket.gethostname())).hostmask)

#port = 13117
#with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as listener:
#    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#    listener.bind((hostmask, port))
#    data, addr = listener.recvfrom(1024)
#    print(addr)
#    print(data)
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    sock.connect(addr)


c = Client()
c.listen_to_udp_messages()