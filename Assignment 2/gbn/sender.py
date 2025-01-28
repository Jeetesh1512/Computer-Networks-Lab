import socket
import threading
import time
import random
from check import *

# Constants
WINDOW_SIZE = 4
TOTAL_FRAMES = 10
TIMEOUT = 3  # seconds
HOST = 'localhost'
PORT = 12346
frameList = makeListOfFrames()  # having the frames list at one place....
# print("ALL THE FRAMES")
# print(frameList)
lock = threading.Lock()

class Sender:
    def __init__(self):
        self.base = 0  # First unacknowledged frame
        self.next_seq_num = 0  # Next sequence number to send
        self.window = WINDOW_SIZE
        self.acks_received = [False] * TOTAL_FRAMES  # To track received ACKs
        self.timer = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)

    def start(self):
        while self.base < TOTAL_FRAMES:
            with lock:
                while self.next_seq_num < self.base + self.window and self.next_seq_num < TOTAL_FRAMES:
                    self.send_frame(self.next_seq_num)
                    self.next_seq_num += 1
                
            self.start_timer()

            try:
                # Waiting for ACK
                ack, _ = self.sock.recvfrom(1024)
                ack = int(ack.decode())
                self.handle_ack(ack)
            except socket.timeout:
                print("Timeout! Resending frames...")
                self.resend_frames()

    def send_frame(self, frame_num):
        message = f"Frame {frame_num}"
        time.sleep(1)
        self.sock.sendto(message.encode(), (HOST, PORT))
        print(f"Sent: {message}")

    def handle_ack(self, ack):
        print(f"Received ACK for Frame {ack}")
        self.acks_received[ack] = True

        with lock:
            if ack == self.base:
                while self.base < TOTAL_FRAMES and self.acks_received[self.base]:
                    self.base += 1
                self.stop_timer()

    def resend_frames(self):
        with lock:
            for i in range(self.base, min(self.base + self.window, TOTAL_FRAMES)):
                self.send_frame(i)
        self.start_timer()

    def start_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(TIMEOUT, self.resend_frames)
        self.timer.start()

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

if __name__ == "__main__":
    sender = Sender()
    t = time.time()
    sender.start()
    print("ALL FRAMES ARE SENT AND ACK ARE RECEIVED!!")
    t1 = time.time() - t ;
    print(f"Total Time :{t1}")
