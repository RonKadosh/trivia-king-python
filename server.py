import socket
import time
import ipaddress
import threading

server_name = 'PokemonTriviaKingByRonKaAndGalHa'
port = 13117

class Server:
    def __init__(self):
        #initializing fields
        self._connections = dict()
        self._state = "waiting_for_clients"

        self._host = socket.gethostbyname(socket.gethostname())
        
        #initializing the TCP socket
        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_sock.bind((self._host, 0))
        self._port = self._tcp_sock.getsockname()[1]
        print(self._port)
    
    def broadcast_offers(self):
        '''The function broadcasts offer messages to join the server'''

        #initializing the UDP broadcast socket       
        broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcaster.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        broadcast_address = str(ipaddress.ip_network(self._host).broadcast_address)
        magic_cookie = 0xabcddcba
        offer = 0x2

        #broadcast message formatting
        to_broadcast = magic_cookie.to_bytes(4,'big')+offer.to_bytes(1,'big')+server_name.encode()+self._port.to_bytes(2,"big")

        #broadcast loop - the loop works until the server state changes
        while self._state == "waiting_for_clients":
            broadcaster.sendto(to_broadcast,(broadcast_address,port))
            print("Server UDP broadcast: " + str(to_broadcast))
            time.sleep(1)

        
    def run(self):
        '''The function runs the server to work, broadcast offers and accept incoming connection. after 10 seconds without any new incoming connection, moving onto the game mode'''

        #initializing the broadcast thread
        broadcast_thread = threading.Thread(group=None, target=self.broadcast_offers, name=None, args=(), kwargs={}, daemon=None)
        broadcast_thread.start()

        #handle incoming connections, timing out the while loop after 10 seconds without new connection
        print("Server started, listening on IP address " + self._host + " for incoming connections...")      
        while self._state == "waiting_for_clients":
            self._tcp_sock.settimeout(10)
            try:
                conn = self._tcp_sock.accept()
                print("here")
            except socket.timeout:
                break
            self._connections[len(self._connections)] = conn
            print(len(self._connections))
        
        #no new connections in the last 10 seconds, starting game mode
        self._state = "game_mode"
        self.game_mode()
        

    def game_mode(self):
        '''The function running the game itself, answering Trivia questions, collecting answers from the clients, and managing the game'''

        print("Welcome to " + server_name + " server, where we are answering Trivia questions about Pokemon!!")
        ##TODO implement game mode

s = Server()
s.run()