import socket
import ipaddress
import struct
import random
import time
import threading
import msvcrt
from abc import ABC, abstractmethod

accepted_keys = ['y', 'Y', 'T', '1', 'n', 'N', 'F', '0']

class Client(ABC):
    def __init__(self, name):
        self._hostmask = str(ipaddress.ip_network(socket.gethostbyname(socket.gethostname())).hostmask)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
        self._closed = False  
        self._name = name + '\n'

    def run(self):
        '''client main loop, stops if failing to connect to server, otherwise never. restarts when connection error occured or when the server side disconnect its socket'''
        while(True):
            try:
                data, addr = self.look_for_server()
                if self.connect_to_server(data, addr):
                    print("Connected to server successfuly! Waiting for the game to start...")
                    self.game_mode()
                else:
                    print("Failed to connect to server, closing Client!")
                    break
            except Exception as e:
                print("Error occured: " + e.strerror + ". Restarting the Client!")
                self._closed = True
                self.reset()
            

    def look_for_server(self):
        '''looking for server udp broadcasts'''
        print("Client started, listening for offer requests...")
        udp_listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_listener.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_listener.bind(('', 13117))
        data, addr = udp_listener.recvfrom(1024)
        print("UDP broadcast recieved: " + str(data) + " from: " + str(addr))
        udp_listener.close()
        return (data, addr)

    def connect_to_server(self, data, addr):
        '''authenticating the connection infront of the server'''
        unpack_format = '>Ih32sH'
        try:
            magic_cookie, offer, server_name, port = struct.unpack(unpack_format, data)
        except struct.error as e:
            print(e)
            return False
        if magic_cookie == 0xabcddcba:
            if offer == 0x2:
                self._sock.connect((addr[0], port))
                self._sock.send(self._name.encode())
                return True
            else:
                print("Offer was not received correctly.")
                return False
        else:
            print("Magic cookie was illegal.")
            return False
    
    @abstractmethod
    def game_mode(self):
        '''game mode, differs between human and bot clients'''
        pass

    def reset(self):
        time.sleep(0.1)
        self._sock.close()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self._closed = False  
    
class HumanClient(Client):
    def __init__(self, name):
        super().__init__(name)
    
    def input_listener(self):
        while not self._closed:        
            msg = msvcrt.getch().decode()
            if msg in accepted_keys:
                self._sock.send(msg.encode())

    def game_mode(self):
        print(self._sock.recv(1024).decode())
        input_listener_thread = threading.Thread(target = self.input_listener)
        input_listener_thread.start()
        while not self._closed:
            print(self._sock.recv(1024).decode())
        input_listener_thread.join()



class BotClient(Client):
    '''Bot Client, assumes that atleast 1 msg is sent at the start of the round and atleast 1 message is sent at the end of the round, and one round starts right after the other'''
    def __init__(self, name):
        super().__init__(name)

    def game_mode(self):
        keys = ['Y', 'N']
        print(self._sock.recv(1024).decode())
        while not self._closed:
            #round starting message
            self._sock.recv(1024)
            print("Message received from server.")
            #sleeping 1 sec to match all servers
            time.sleep(1)
            random_key = keys[random.randint(0,1)]
            print("Randomizing answer: [" + random_key + "] and sending it to server.")
            self._sock.send(random_key.encode())
            #round ending msg
            self._sock.recv(1024)

