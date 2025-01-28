import socket
from Crypto.Util.number import bytes_to_long, long_to_bytes
import random
import time
import checksum
import crc
import helper

HOST = 'localhost'
PORT = 3000
c = socket.socket()
random.seed(time.time())

def inject_error(text: str, number: int) -> str:
    if number == 0:
        return text
    for _ in range(number):
        x = random.randint(0, len(text) - 1)
        if text[x] == '0':
            text = text[:x] + '1' + text[x + 1:]
        else:
            text = text[:x] + '0' + text[x + 1:]
    return text

def inject_error_2(text: str , num) -> str:
    #CRC_1 is x+1 and by inserting 11 at the end the codeword becomes divisible by x+1 and thus CRC is not able to detect the error 
    modified_text = '0' * (len(text) - 2) + "11"
    return modified_text


c.connect((HOST, PORT))

text = input("Enter data:").encode('utf-8')
res = input("Do you want to insert errors?(Y/n)")
enc_text = bin(bytes_to_long(text))[2:]
actual_len = len(enc_text)

if actual_len % 8 != 0:
    extra = '0' * (8 - (actual_len % 8))
    enc_text += extra

c.send(long_to_bytes(actual_len))
time.sleep(1)

print("CRC Method In Progress")
c.send(b"CRC")
time.sleep(1)
crc_method = input("Give the CRC divisor method:")
divisor = helper.convToBinary(crc_method)
c.send(divisor.encode('utf-8'))

PKT_SIZE_CRC = 8

# crc_chunks = []
# for i in range(0, len(enc_text), PKT_SIZE_CRC):
#     crc_chunks = enc_text[i:i + PKT_SIZE_CRC]

crc_chunks = [enc_text[i:i + PKT_SIZE_CRC] for i in range(0, len(enc_text), PKT_SIZE_CRC)]
crc_encoded_chunks = crc.CRC.encodeData(crc_chunks, divisor)

for chunk in crc_encoded_chunks:
    time.sleep(1)
    if res.lower() == 'y':
        injected_chunk = inject_error(chunk, random.randint(0, 2)) #if inject_error_2 crc1 doesn't work
        c.send(injected_chunk.encode('utf-8'))
    else:
        c.send(chunk.encode('utf-8'))

c.send(b'EOF')
crc_result = c.recv(1024).decode('utf-8')
print(f"CRC Result: {crc_result}")

time.sleep(2)

c.send(long_to_bytes(actual_len))
print("Checksum Method In Progress")
c.send(b"Checksum")
time.sleep(1)

PKT_SIZE_CHECKSUM = 16
swap_flag = True   #if it is True then checksum will not work

checksum_chunks = [enc_text[i:i + PKT_SIZE_CHECKSUM] for i in range(0, len(enc_text), PKT_SIZE_CHECKSUM)]
checksum_value = checksum.Checksum.generate_checksum(checksum_chunks)
c.send(checksum_value.encode('utf-8'))
if swap_flag and len(checksum_chunks) > 1:
    checksum_chunks[0], checksum_chunks[-1] = checksum_chunks[-1], checksum_chunks[0]

for chunk in checksum_chunks:
    time.sleep(1)
    if not swap_flag and res.lower() == 'y':
        injected_chunk = inject_error(chunk, random.randint(0, 2))
        c.send(injected_chunk.encode('utf-8'))
    else:
        c.send(chunk.encode('utf-8'))
c.send(b'EOF')

checksum_result = c.recv(1024).decode('utf-8')
print(f"Checksum Result: {checksum_result}")

c.send(b'EOF')
c.close()
