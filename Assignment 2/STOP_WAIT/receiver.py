import socket
import time

SOURCE_ADDRESS = "011011"       
DESTINATION_ADDRESS = "110110"
PAYLOAD_SIZE = 8                  
CHECKSUM_SIZE = 4                 

RECEIVER_IP = '127.0.0.1'
RECEIVER_PORT = 5005


def setWrapSum(sum):
    temp =sum
    if(sum > 0xF):
        temp = temp & 0xF0
        temp = temp>>4
        sum += temp
        sum = sum & 0x0F
    return sum

def calculate_checksum(data):
    sum =0
    for i in range(0,len(data),4):
        byte = data[i:i+4]
        sum += int(byte,2)
    wrapsum = setWrapSum(sum)
    checksum = (~wrapsum & 0xF)
    #print(f"Checksum at RECV:{format(checksum,'04b')}")
    return format(checksum,'04b')

def receive_data():
    
    # Initialize TCP socket
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    receiver_socket.bind((RECEIVER_IP, RECEIVER_PORT))
    receiver_socket.listen(1)
    print(f"Receiver is listening on {RECEIVER_IP}:{RECEIVER_PORT}")

    conn, addr = receiver_socket.accept()
    print(f"Connected by {addr}")

    expected_seq_num = 0  # Initial expected sequence number

    while True:
        try:
            frame = conn.recv(1024)
            if not frame:
                continue
            
            Frame = frame.decode()
            print("Received data is :",Frame,"  ",len(Frame))
            #padding = Frame[0:7]
            src = Frame[7:13]
            dest = Frame[13:19]
            size = Frame[19:23]
            seq = Frame[23:24]
            data = Frame[24:32]
            fcs = Frame[32:36]

            calculated_checksum = calculate_checksum(Frame[0:32])
            #print("fcs -----",fcs)
            if calculated_checksum != fcs:
                print("Checksum mismatch. Frame corrupted. Discarding frame.")
                continue  # Discard the frame and do not send ACK

            if src != SOURCE_ADDRESS or dest != DESTINATION_ADDRESS:
                print("Invalid source or destination address. Discarding frame.")
                continue  # Invalid addresses
            
            if seq != str(expected_seq_num):
                print(f"Unexpected sequence number. Expected: {expected_seq_num}, Received: {seq}. Discarding frame.")
                continue  # Discard out-of-order frame

            print(f"Received Frame Seq: {seq}, Payload: {data}")

            ack_packet = f"{expected_seq_num}ACK".encode()
            time.sleep(1)
            conn.sendall(ack_packet)
            print(f"Sent ACK for Seq#: {expected_seq_num}")

            # Update expected sequence number
            expected_seq_num = 1 - expected_seq_num

        except KeyboardInterrupt:
            print("\nReceiver shutting down.")
            break

    conn.close()
    receiver_socket.close()

if __name__ == "__main__":
    receive_data()
