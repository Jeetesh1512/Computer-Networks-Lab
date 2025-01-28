import socket
import random

WINDOW_SIZE = 4
PROBABILITY_CORRUPTION = 0.1  # Probability of corrupted ACK/NACK
#PROBABILITY_CORRUPTION = -1  #channel is ideal
class Receiver:
    def __init__(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((ip, port))
        self.window = [-1] * WINDOW_SIZE
        self.expected_seq_num = 0

    def send_ack(self, addr, seq_num, status):
        print(f"Sending {status} for frame {seq_num}")
        if random.random() < PROBABILITY_CORRUPTION:
            print(f" ***ACK {seq_num}  LOST***")
            return
        self.sock.sendto(f"{seq_num}:{status}".encode(), addr)

    def receive_frame(self):
        while True:
            frame, addr = self.sock.recvfrom(1024)
            frame = frame.decode()
            seq_num, data = frame.split(":")
            seq_num = int(seq_num)

            if data == "CORRUPT":
                print(f"Frame {seq_num} is corrupt, sending --------NACK")
                self.send_ack(addr, seq_num, "NACK")
            elif seq_num == self.expected_seq_num:
                print(f"Received correct frame {seq_num}, sending ACK")
                self.send_ack(addr, seq_num, "ACK")
                self.expected_seq_num += 1
            else:
                print(f"Out of order frame {seq_num}, sending ACK")
                self.send_ack(addr, seq_num, "ACK")

if __name__ == "__main__":
    receiver = Receiver("localhost", 12345)
    receiver.receive_frame()
