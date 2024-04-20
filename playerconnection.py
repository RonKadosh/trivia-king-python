import threading
import socket
import time
import re
from logger import Logger

def validate_name(name):
    # Regular expression pattern for validating names
    pattern = r'^[a-zA-Z]{2,25}(?:\s[a-zA-Z]{2,25})?\n$'
    return bool(re.match(pattern, name))

class PlayerConnection:
    '''Connection Handler, running a Thread for each player socket'''

    @staticmethod
    def validate_name(name):
        # Regular expression pattern for validating names
        pattern = r'^[a-zA-Z]{2,25}(?:\s[a-zA-Z]{2,25})?\n$'
        return bool(re.match(pattern, name))

    def __init__(self, sock, addr, id, server_msg_q, name):
        self._socket = sock
        self._socket.setblocking(True)
        self._socket.settimeout(None)
        self._addr = addr
        self._id = id
        self._server_msg_q = server_msg_q
        self._active = True
        self._name = name
        self._condition = threading.Condition()
        self._thread = threading.Thread(target = self.run, name = "SERVER - SOCKET ID [" + str(id) + "] THREAD")
        self._thread.start()


    def is_active(self):
        return self._active

    def get_id(self):
        return self._id

    def get_name(self):
        return self._name

    def notify(self):
        with self._condition:
            self._condition.notify()

    def run(self):
        try:
            while(self._active):
                #handle incoming message
                incoming_msg = self._socket.recv(1)
                Logger.log(threading.current_thread().getName(), "Message received: " + str(incoming_msg))
                with self._condition:
                    self._condition.wait()
                self._server_msg_q.put((self._id, incoming_msg.decode()))

                #empty the buffer after sending the msg to the msg queue
                self._socket.setblocking(False)
                while(True):
                    try:
                        self._socket.recv(2048)
                    except BlockingIOError:
                        self._socket.setblocking(True)
                        break
        except Exception as e:
            Logger.log(threading.current_thread().getName(), "Exception occured: " + e.strerror + ". Closing the connection!")
            self._active = False
                
    def send(self, msg, to_all):
        if to_all:
            self._socket.send(msg.encode())

    def close(self):
        self.notify()
        self._socket.close()