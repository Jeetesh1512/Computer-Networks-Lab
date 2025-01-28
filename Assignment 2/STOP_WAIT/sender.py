import socket
import time
import random

SOURCE_ADDRESS = "011011"                                 #CAPITAL letters are constant
DESTINATION_ADDRESS = "110110"
PAYLOAD_SIZE = 8                  
CHECKSUM_SIZE = 4                 

TIMEOUT = 2                   
MAX_RETRIES = 5                   

RECEIVER_IP = '127.0.0.1'
RECEIVER_PORT = 5005

PACKET_CORRUPTION_PROBABILITY = 0.99
DELAY_RANGE = (0.5, 0.9)             # Delay between 100ms and 500ms

def setWrapSum(sum):
    temp =sum
    if(sum > 0xF):
        temp = temp & 0xF0
        temp = temp>>4
        sum += temp
        sum = sum & 0x0F
    return sum

def calculate_checksum(header):
    sum = 0
    for i in range(0,len(header),4):
        byte = header[i:i+4]
        sum += int(byte,2)
    wrapsum = setWrapSum(sum)
    checksum = (~wrapsum & 0xF)
    #print(f"Checksum at sender:{format(checksum,'04b')}")
    return format(checksum,'04b')

def create_frame(seq_num, payload):
    
    length = len(payload)
    header = SOURCE_ADDRESS+DESTINATION_ADDRESS+"1000"+str(seq_num);
    frame_without_fcs = "0000000"+header+payload
    fcs = calculate_checksum(frame_without_fcs)
    frame = frame_without_fcs + fcs   #using checksum.....
    return frame

def inject_errors(frame):
    if random.random() < PACKET_CORRUPTION_PROBABILITY:       #[0,1)
        frame = list(frame)
        char_index = random.randint(0, len(frame) - 1)
        frame[char_index] = "1" if frame[char_index] == "0" else "0" 
        frame = ''.join(frame)
    return frame

def delay():
    delay = random.uniform(*DELAY_RANGE)
    time.sleep(delay)

def send_data(file_path):
    # Initialize TCP socket
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender_socket.connect((RECEIVER_IP, RECEIVER_PORT))
    sender_socket.settimeout(TIMEOUT)

    seq_num = 0  

    try:
        with open(file_path, 'r') as file:
            while True:
                payload = file.readline()
                if not payload:
                    print("All data has been sent.")
                    break  # EOF
                payload = payload.rstrip('\n') 
                #print(f"DATA IS:{payload}")
                binarydata = bin(int(payload, 16))[2:]
                db = ""
                if(8 - len(binarydata)>0):
                    l = 8 - len(binarydata);
                    for i in range(l):
                        db +="0";    
                db += (binarydata)
                    
                #print(db)
                frame = create_frame(seq_num,db)
                retries = 0  
                Frame = frame
                #print(f"SENDING FRAME : {Frame}")
                while retries < MAX_RETRIES:
                    delay()

                    # if(retries > 1):                                         #after 2 retries the correct data will be sent...
                    #     corrupted_frame = Frame
                    # else:
                    #     corrupted_frame = inject_errors(frame)
                    corrupted_frame = Frame
                    print("Sending data is :",corrupted_frame,"  ",len(corrupted_frame))
                    sender_socket.sendall(corrupted_frame.encode('utf-8'))
                    print(f"Sent Frame Seq#: {seq_num}, Payload: {db}")

                    try:
                        # Wait for ACK
                        ack_packet = sender_socket.recv(1024)
                        ak = ack_packet.decode('utf-8')
                        #print("AK-",ak)
                        if ak[0] == str(seq_num):
                            print(f"Received ACK for Seq: {ak[0]}\n")
                            seq_num = 1 - seq_num  
                            break 
                        else:
                            print(f"Received invalid ACK: {ack_packet}\n")
                    except socket.timeout:
                        retries += 1
                        print(f"Timeout waiting for ACK for Seq: {seq_num}. Retrying ({retries}/{MAX_RETRIES})...\n")

                if retries == MAX_RETRIES:
                    print(f"Failed to receive ACK for Seq#: {seq_num} after {MAX_RETRIES} attempts. Exiting.")
                    return

    except FileNotFoundError:
        print(f"File {file_path} not found.")
    finally:
        sender_socket.close()

if __name__ == "__main__":
    t = time.time()
    send_data("inputdata.txt")
    print("ALL FRAMES ARE SENT AND ACK ARE RECEIVED!!")
    t1 = time.time() - t ;
    print(f"Total Time :{t1}")
    
