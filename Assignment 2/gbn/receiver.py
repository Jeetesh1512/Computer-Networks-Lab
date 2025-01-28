import socket
import random
import time
from check import *

# Constants
TOTAL_FRAMES = 10
HOST = 'localhost'
PORT = 12346
PACKET_CORRUPTED_PROBABILITY = 0.05 # probabilty for having the corrupted data..

class Receiver:
    def __init__(self):
        self.expected_frame = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((HOST, PORT))

    def start(self):
        while self.expected_frame < TOTAL_FRAMES:
            frame, addr = self.sock.recvfrom(1024)
            frame_num = int(frame.decode().split()[1])
            print(f"Received: {frame.decode()}")

            if random.random() < PACKET_CORRUPTED_PROBABILITY:  # 10% chance of frame loss
                print(f"Frame {frame_num} is lost!")
                continue
            
            if checkTheChecksum() < PACKET_CORRUPTED_PROBABILITY:
                print(f"Frame {frame_num} is wrong!")
                continue
            if frame_num == self.expected_frame:
                print(f"ACK Sent for Frame {self.expected_frame}")
                self.sock.sendto(str(self.expected_frame).encode(), addr)
                self.expected_frame += 1
            else:
                print(f"Discarding frame {frame_num}, waiting for {self.expected_frame}")

if __name__ == "__main__":
    receiver = Receiver()
    receiver.start()
