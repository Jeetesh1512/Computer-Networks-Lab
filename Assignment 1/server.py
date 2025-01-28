import socket
from Crypto.Util.number import long_to_bytes, bytes_to_long
import checksum
import crc

s = socket.socket()
s.bind(('localhost', 3000))
s.listen(1)
print("Waiting for connections")

while True:
    c, addr = s.accept()
    print("Connection from {}".format(addr))
    for i in range (2):
        try:
            size = bytes_to_long(c.recv(1024))
            print(f"Data size received: {size}")

            method = c.recv(1024).decode('utf-8')
            print(f"Detection method received: {method}")

            li = []

            if method == "CRC":
                
                divisor = c.recv(1024).decode('utf-8')
                print(f"CRC divisor received: {divisor}")

                
                while True:
                    text = c.recv(1024).decode('utf-8')
                    print(text + "\n")
                    if 'EOF' in text:
                        li.append(text.replace("EOF", ""))
                        print("end")
                        break
                    li.append(text)

                received_text = ''.join(li)[:size]
                print("Received Data (CRC)={}".format(received_text))
                
                if crc.CRC.checkRemainder(li, divisor):
                    c.send(b"Received Text, No errors found by CRC")
                else:
                    c.send(b"Error detected by CRC")

            elif method == "Checksum":

                checksum_value = c.recv(1024).decode('utf-8')
                print(f"Checksum value received: {checksum_value}")

                while True:
                    text = c.recv(1024).decode('utf-8')
                    if 'EOF' in text:
                        li.append(text.replace("EOF", ""))
                        break
                    li.append(text)

                received_text = ''.join(li)[:size]
                print("Received Data (Checksum)={}".format(received_text))

                if checksum.Checksum.check_checksum(li, checksum_value):
                    c.send(b"Received Text, No errors found by Checksum")
                else:
                    c.send(b"Error detected by Checksum")

            else:
                raise Exception("Invalid detection method received")

        except Exception as e:
            print(f"Error: {e}")
    
    
