import binascii
import socket
import struct
import sys
import hashlib
import random
import time

UDP_IP = '127.0.0.1'
UDP_PORT = 5005

# create the socket and listen for incoming connections
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

responseSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("server active and listening for incoming connections\n")

# setup unpacker
unpacker = struct.Struct("I I 8s 32s")
# UDP_Data1 = struct.Struct('I I')
UDP_Data2 = struct.Struct('I I 32s')

#introduce server side delays and losses.
def Network_Delay():
    if True and random.choice([0,1,0]) == 1: # Set to False to disable Network Delay. Default is 33% packets are delayed
       time.sleep(.01)
       print("Packet Delayed")
    else:
        print("Packet Sent")

def Network_Loss():
    if True and random.choice([0,1,1,0]) == 1: # Set to False to disable Network Loss. Default is 50% packets are lost
        print("Packet Lost")
        return(1)
    else:
        return(0)


def Packet_Checksum_Corrupter(packetdata):
    if True and random.choice(
            [0, 1, 0, 1]) == 1:  # # Set to False to disable Packet Corruption. Default is 50% packets are corrupt
        return (b'Corrupt!')
    else:
        return (packetdata)

#keep listening for incoming connections
while True:

    print("---------------------------------------------------------------")
    responseSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    data, addr = sock.recvfrom(1024)

    UDP_Packet = unpacker.unpack(data)

    # print packet data
    print("Received packet data from client")
    print(UDP_Packet[0], UDP_Packet[1], UDP_Packet[2], UDP_Packet[3])
    SEQ=UDP_Packet[1]

    # create checksum for comparison
    values = (UDP_Packet[0], UDP_Packet[1], Packet_Checksum_Corrupter(UDP_Packet[2]))
    packer = struct.Struct('I I 8s')
    packed_data = packer.pack(*values)
    chkSum = bytes(hashlib.md5(packed_data).hexdigest(), encoding="UTF-8")

    if UDP_Packet[3] == chkSum:
        print("chkSums Match\n")
        if UDP_Packet[1] == 1:
            SEQ = 0
        else:
            SEQ = 1

        # create checksum
        values = (UDP_Packet[0], SEQ)
        chkSumStruct = struct.Struct('I I')
        chkSumData = chkSumStruct.pack(*values)
        chkSum = bytes(hashlib.md5(chkSumData).hexdigest(), encoding="UTF-8")

        # create response packet
        responseVal = (UDP_Packet[0], SEQ, chkSum)
        UDP_Packet = UDP_Data2.pack(*responseVal)
        #method to randomly delay the server response
        Network_Delay()
        Network_Loss()
        responseSocket.sendto(UDP_Packet, (UDP_IP, 5004))
        responseSocket.close()

    else:
        print("chkSums do not match\n")
        if UDP_Packet[0] == 1:
            ACK = 0
        else:
            ACK = 1

        # create checksum
        values = (ACK, SEQ)
        chkSumStruct = struct.Struct('I I')
        chkSumData = chkSumStruct.pack(*values)
        chkSum = bytes(hashlib.md5(chkSumData).hexdigest(), encoding="UTF-8")

        # # create response packet
        responseVal = (ACK, SEQ, chkSum)
        UDP_Packet = UDP_Data2.pack(*responseVal)
        Network_Delay()
        Network_Loss()
        responseSocket.sendto(UDP_Packet, (UDP_IP, 5004))
        responseSocket.close()

        print("Sending ACK to show packet is corrupt\n")
