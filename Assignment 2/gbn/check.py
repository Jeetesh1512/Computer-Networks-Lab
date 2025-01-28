import time
import random

SOURCE_ADDRESS = "011011"                                 #CAPITAL letters are constant
DESTINATION_ADDRESS = "110110"
PAYLOAD_SIZE = 8                  
CHECKSUM_SIZE = 4                 

TIMEOUT = 2                   
MAX_RETRIES = 5                   


PACKET_CORRUPTION_PROBABILITY = 0.6

def setWrapSum(sum):
    temp =sum
    if(sum > 0xF):
        temp = temp & 0xF0
        temp = temp>>4
        sum += temp
        sum = sum & 0x0F
    return sum

def calculate_checksum(header):
    sum =0
    for i in range(0,len(header),4):
        byte = header[i:i+4]
        sum += int(byte,2)
    wrapsum = setWrapSum(sum)
    checksum = (~wrapsum & 0xF)
    #print(f"Checksum at sender:{format(checksum,'04b')}")
    return format(checksum,'04b')
def checkTheChecksum():
    return random.random()
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

def makeListOfFrames():
    file = open("inputdata.txt","r")
    line = file.readline().strip()
    frameList =[]
    i = 0;
    while(line):
        frameList.append(create_frame(i%4,line))
        line = file.readline().strip()
    return frameList