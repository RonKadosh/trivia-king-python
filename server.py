import socket
import time
import ipaddress
import threading
import struct
import queue
import playerconnection
import gamemanager
from logger import Logger


server_name = 'PokemonTriviaKingByRonKaAndGalHa'
broadcast_port = 13117

#time to broadcast since last connection in seconds
broadcast_time = 10
sec = 1

#wait for name to be sent after connection
wait_for_name = 0.1

#time of round in seconds
round_time = 10


class Server:
    def __init__(self):
        #initializing fields
        threading.current_thread().setName("SERVER - MAIN THREAD")
        self._connections = dict()
        self._msg_q = queue.Queue()
        self._waiting_for_clients = True
        self._id_distributor = 0
        
        #initializing the TCP socket
        self._tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #listen to all network interfaces
        self._tcp_sock.bind(('', 0))
        self._port = self._tcp_sock.getsockname()[1]
        self._tcp_sock.listen()

        #bonus field - leaderboard

        self._leaderboard = list()
        for i in range(10):
            self._leaderboard.append(('NONE', 0))
        
        Logger.log(threading.current_thread().getName(), "Starting and now is ready for incoming connections...")
    
    def notify_all(self):
        for conn in self._connections.values():
            if conn.is_active():
                conn.notify()

    def send(self, msg, cid):
        self._connections[cid].send(msg, False)
    
    def send_all(self, msg):
        for conn in self._connections.values():
            if conn.is_active():
                conn.send(msg, True)
        Logger.log(threading.current_thread().getName(), "Sending message to all active connections: " + msg)

    def broadcast_offers(self):
        '''The function broadcasts offer messages to join the server'''
        #initializing the UDP broadcast socket       
        broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        #broadcast message formatting
        pack_format = '>Ih32sH'
        to_broadcast = struct.pack(pack_format, 0xabcddcba, 0x2, server_name.encode(), self._port)

        #broadcast loop - the loop works until the server state changes
        while self._waiting_for_clients:
            #broadcaster.sendto(to_broadcast,(broadcast_address,broadcast_port))
            broadcaster.sendto(to_broadcast,('<broadcast>',broadcast_port))
            Logger.log(threading.current_thread().getName(), "Broadcasting on UDP: " + str(to_broadcast))
            time.sleep(1)
        
        broadcaster.close()

        
    def run(self):
        '''The function runs the server, broadcast offers and accept incoming connection. after 10 seconds without any new incoming connection, moving onto the game mode'''
        while(True):
            self.waiting_for_clients()
            self.game_mode()
            self.reset()

        
    def waiting_for_clients(self):
        #initializing the broadcast thread
        broadcast_thread = threading.Thread(target=self.broadcast_offers, name = "SERVER - BROADCASTING THREAD", daemon=True)
        broadcast_thread.start()

        #handle incoming connections, timing out the while loop after 10 seconds without new connection     
        while True:            
            try:
                conn, addr = self._tcp_sock.accept()               
            except socket.timeout:
                break
            
            #creating a threaded blocking connection handler for each client if the name is valid, else reject the socket connection
            try:
                conn.setblocking(True)
                conn.settimeout(wait_for_name)         
                Logger.log(threading.current_thread().getName(), "New client connected on: " + str(addr) + "     ID: [" + str(self._id_distributor) + "]")
                Logger.log(threading.current_thread().getName(), "Authenticating...")
                #here is waiting for the predefined and sent name of the client 0.1sec since ping in the LAN is around 3ms so 0.1 is more than enough to wait
                name = conn.recv(1024).decode()
                if playerconnection.PlayerConnection.validate_name(name):
                    self._connections[self._id_distributor] = playerconnection.PlayerConnection(conn, addr, self._id_distributor, self._msg_q, name[0:-1])
                    Logger.log(threading.current_thread().getName() , "Client ID [" + str(self._id_distributor) + "] has connected succesfuly!" )
                    self._id_distributor+=1
                    #waiting for another 10 seconds since last sucessful connection 
                    self._tcp_sock.settimeout(broadcast_time)
                else:
                    #name not valid -> close the connection
                    Logger.log(threading.current_thread().getName(), "Client on: " + str(addr) + " has sent illegal name (Format 2-25 chars long ending with backslash n), closing the connection!")
                    conn.close()
            except BlockingIOError:
                #name did not sent -> close the connection
                Logger.log(threading.current_thread().getName(), "Client on: " + str(addr) + " did not send his name immediately, closing the connection!")
                conn.close()
        
        
        self._waiting_for_clients = False
        broadcast_thread.join()
            
            


    def game_mode(self):
        '''The function running the game itself, sending Trivia questions to the players, collecting answers from the clients, and managing the game'''
        self.send_all("Welcome to " + server_name + " server, where we answer trivia questions about Pokemon!\n\n")
        #first creating a GameManager obj and adding all the clients as players to it
        gm = gamemanager.GameManager()
        for conn in self._connections.values():
            if conn.is_active():
                gm.add_player(conn.get_id(), conn.get_name())

        #game loop, gathering answers until timout, checking the correctness and sending messages to clients
        while gm.game_active() and len(list(filter(lambda conn: conn.is_active(), self._connections.values())))>0:
            self.send_all(gm.round_init())
            self.send_all(gm.choose_question())
            time.sleep(round_time - sec)
            #waking up the socket threads - to put their ans in the msg_q 
            self.notify_all()
            time.sleep(sec)
            while True:
                try:
                    msg = self._msg_q.get(block = False)
                    id = msg[0]
                    ans = msg[1]
                    if ans in ['y', 'Y', '1', 'T']:
                        ans = True  
                    elif ans in ['n', 'N', '0', 'F']:
                        ans = False
                    else:
                        Logger.log("GM" , "Received illegal answer from the player ID [" + str(id) + "]: " + str(ans))
                        continue
                    gm.gather_answer(id, ans)
                except queue.Empty:
                    break
                
            self.send_all(gm.sum_round())
        
        #exiting the while loop means the game has ended

        #bonus purpose, leaderboards update
        for name, score in gm.sum_game():
            for i in range(0,10):
                if score > self._leaderboard[i][1]:
                    self._leaderboard.insert(i, (name, score))
                    self._leaderboard.pop()
                    break
        
        self.send_all(self.leader_board_string())
            
                
    def leader_board_string(self):
        leader_board_string = 'LEADERBOARD      NAME                     SCORE\n===========      ====                     =====\n\n'
        count = 1
        for name,score in self._leaderboard:
            pad2 = " "*(25-len(name))
            pad1 = " "*15
            if count == 10:
                pad1 = " "*14
            leader_board_string += str(count) + "." + pad1 + name + pad2 + str(score) + "\n"
            count+=1
        return leader_board_string

         
    def reset(self):
        '''The functions resets the server: closing the open connections and readies the server for another round.'''
        time.sleep(sec)
        for conn in self._connections.values():
            conn.close()
        Logger.log(threading.current_thread().getName(), "Game over, sending out offer requests...")
        self._connections = dict()
        self._msg_q = queue.Queue()
        self._id_distributor = 0
        self._waiting_for_clients = True
        self._tcp_sock.settimeout(None)
        time.sleep(sec)
        

s = Server()
s.run()