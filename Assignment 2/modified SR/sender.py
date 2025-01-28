import socket
import threading
import random
import time

# Configuration
WINDOW_SIZE = 4
PROBABILITY_CORRUPTION = 0.1  # Probability of frame corruption
#PROBABILITY_CORRUPTION = -1  #channel is ideal
TIMEOUT = 5  # seconds

class Frame:
    def __init__(self, seq_num, data):
        self.seq_num = seq_num
        self.data = data

class Sender:
    def __init__(self, receiver_ip, receiver_port):  #for the intialization of everything required....
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.window = []
        self.next_seq_num = 0
        self.base = 0
        self.frames = self.readfromfile("inputdata.txt")
        self.TOTAL_FRAMES = len(self.frames)
        self.ack_received = [False] * self.TOTAL_FRAMES

    def readfromfile(self, frame_file):
        frames = []
        with open(frame_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                frames.append(Frame(i, line.strip()))  # Treat each binary line as a frame
        return frames

    def send_frame(self, frame):
        if random.random() < PROBABILITY_CORRUPTION:
            print(f"******Frame {frame.seq_num} corrupted******")
            corrupted_frame = Frame(frame.seq_num, "CORRUPT")
            time.sleep(1)
            self.sock.sendto(f"{corrupted_frame.seq_num}:{corrupted_frame.data}".encode(), (self.receiver_ip, self.receiver_port))
        else:
            print(f"Sending frame {frame.seq_num}: {frame.data}")
            time.sleep(0.5)
            self.sock.sendto(f"{frame.seq_num}:{frame.data}".encode(), (self.receiver_ip, self.receiver_port))

    def resend_frame(self, seq_num):
        for frame in self.window:
            if frame.seq_num == seq_num:
                print(f"Resending frame {seq_num}++")
                self.send_frame(frame)

    def receive_ack(self):
        while self.base < self.TOTAL_FRAMES:
            try:
                ack, _ = self.sock.recvfrom(1024)
                ack = ack.decode()
                print(f"Received {ack}")
                ack_num, status = ack.split(":")
                ack_num = int(ack_num)

                if status == "ACK":
                    self.ack_received[ack_num] = True
                    if ack_num == self.base:
                        while self.base < self.TOTAL_FRAMES and self.ack_received[self.base]:
                            self.base += 1
                            if self.next_seq_num < self.TOTAL_FRAMES:
                                frame = self.frames[self.next_seq_num]
                                self.window.append(frame)
                                self.send_frame(frame)
                                self.next_seq_num += 1
                            self.window = self.window[1:]  # Slide window
                elif status == "NACK":
                    print(f"Received NACK for frame {ack_num}")
                    self.resend_frame(ack_num)

            except socket.timeout:
                print("Timeout, resending unacknowledged frames")
                for i in range(self.base, self.base + WINDOW_SIZE):
                    if i < self.TOTAL_FRAMES and not self.ack_received[i]:
                        self.resend_frame(i)

    def start(self):  #starting the transmission....
        for i in range(min(WINDOW_SIZE, self.TOTAL_FRAMES)):
            frame = self.frames[i]
            self.window.append(frame)
            self.send_frame(frame)
            self.next_seq_num += 1

        ack_thread = threading.Thread(target=self.receive_ack)
        ack_thread.start()
        ack_thread.join()

if __name__ == "__main__":
    sender = Sender("localhost", 12345)
    t = time.time()
    sender.start()
    print("ALL FRAMES ARE SENT AND ACK ARE RECEIVED!!")
    t1 = time.time() - t ;
    print(f"Total Time :{t1}")