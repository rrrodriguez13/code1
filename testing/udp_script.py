import numpy as np
import socket
import sys
import threading
import time

MAX_UDP_PACKET_SIZE = 2048 # Maximum safe UDP packet size

class send:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def stop(self):
        self.s.close()
    
    def eth0(self):
        self.s.connect((self.HOST, self.PORT))
        print('eth0 starting...')
        
    
    def send_data(self, data):
        data = np.array(data, dtype=np.uint8).tobytes()  # Ensures data is bytes
        chunks = np.reshape(data, (-1, MAX_UDP_PACKET_SIZE))
        for i, chunk in enumerate(chunks):
            self.s.sendto(chunks, (self.HOST, self.PORT))
            print(f'Sent chunk {i+1}/{len(chunks)} of size {len(chunk)}')

class receive:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(5)
        print("new version")
        print(self.HOST)
        print(self.PORT)

    def eth0(self):
        self.s.bind((self.HOST, self.PORT))
        #self.s.listen()
        #self.conn, addr = self.s.accept()
        print(f'Listening on port {self.PORT} ...')
    
    def set_up(self):
        try:
            print('Waiting to receive data ...')
            data, addr = self.s.recvfrom(MAX_UDP_PACKET_SIZE)
            #print(f'Received data: {len(data)} bytes from {addr}')
            print('Received data!\n')
        except socket.timeout:
            print('No data received, waiting for next packet ...')
            print("\n")
    
    def stop(self):
        self.s.close()
