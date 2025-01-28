
# import sys
# import datetime
# from packetManager import Packet

# class Receiver:
#     def __init__(self, id: int, channelToReceiver) -> None:
#         self.seq = 0 #must be synced with sender seq
#         self.id = id
#         self.sender_dict = {} # key value pair of sender_id:outfile_path
#         self.channelToReceiver = channelToReceiver

#     def write_file(self, filename: str):
#         try:
#             fd = open(filename, "a+")
#         except FileNotFoundError as err:
#             current_time = datetime.datetime.now()
#             print(f"\n [{current_time.strftime('%d/%m/%Y %H:%M:%S')}] ERROR: {err} File {filename} not found!")
#             sys.exit(f"File {filename} Not Found!")
#         return fd

#     def init_receiver(self):
#         while True:
#             packet = self.channelToReceiver.recv()
#             sender = packet.get_src()
#             if sender not in self.sender_dict.keys():
#                 self.sender_dict[sender] = "./logs/output/output" + str(sender+1) + '.txt'

#             outfile = self.sender_dict[sender]
#             fd = self.write_file(outfile)
#             datastr = packet.get_data()
#             fd.write(datastr)
#             fd.close()
#             current_time = datetime.datetime.now()
#             with open("logs/log.txt", "a+") as f:
#                 f.write(f"\n[{current_time.strftime('%d/%m/%Y %H:%M:%S')}] Receiver-{self.id+1} received Packet SUCCESSFULLY!\n")


import sys
import datetime
from packetManager import Packet

class Receiver:
    def __init__(self, id: int, channelToReceiver) -> None:
        self.seq = 0  # must be synced with sender seq
        self.id = id
        self.sender_dict = {}  # key-value pair of sender_id: outfile_path
        self.channelToReceiver = channelToReceiver

    def write_file(self, filename: str):
        try:
            # Open the file in append mode, creating it if it doesn't exist
            fd = open(filename, "a+", encoding='utf-8')
        except FileNotFoundError as err:
            current_time = datetime.datetime.now()
            print(f"\n[{current_time.strftime('%d/%m/%Y %H:%M:%S')}] ERROR: {err} File {filename} not found!")
            sys.exit(f"File {filename} Not Found!")
        except IOError as io_err:
            # Handle other IO-related errors (like permission issues)
            current_time = datetime.datetime.now()
            print(f"\n[{current_time.strftime('%d/%m/%Y %H:%M:%S')}] ERROR: {io_err} Unable to open {filename}!")
            sys.exit(f"Unable to open {filename}!")
        return fd

    def init_receiver(self):
        while True:
            packet = self.channelToReceiver.recv()
            sender = packet.get_src()
            if sender not in self.sender_dict:
                # Generate the output file path for each sender
                self.sender_dict[sender] = f"./logs/output/output{sender+1}.txt"

            outfile = self.sender_dict[sender]
            fd = self.write_file(outfile)

            # Get the data from the packet and handle any decode issues
            try:
                datastr = packet.get_data()  # This could raise UnicodeDecodeError
            except UnicodeDecodeError as decode_err:
                # Log and handle decode errors here
                current_time = datetime.datetime.now()
                print(f"\n[{current_time.strftime('%d/%m/%Y %H:%M:%S')}] ERROR: Unable to decode data from sender {sender}")
                with open("logs/log.txt", "a+") as f:
                    f.write(f"\n[{current_time.strftime('%d/%m/%Y %H:%M:%S')}] ERROR: UnicodeDecodeError while decoding data from sender {sender}\n")
                datastr = ''  # You can handle this based on your use case

            fd.write(datastr)
            fd.close()

            # Log the successful reception of the packet
            current_time = datetime.datetime.now()
            with open("logs/log.txt", "a+") as f:
                f.write(f"\n[{current_time.strftime('%d/%m/%Y %H:%M:%S')}] Receiver-{self.id+1} received Packet SUCCESSFULLY from sender {sender}!\n")
