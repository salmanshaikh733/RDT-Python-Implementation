import socket
import hashlib
import struct
import sys
import binascii

# set port and ip
UDP_IP = "127.0.0.1"
UDP_Port = 5005

# create packer
UDP_Packet_Data = struct.Struct('I I 8s 32s')
clientUnpacker = struct.Struct('I I 32s')

ACK = 0
SEQ = 0

# create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

dataList = ['NCC-1701', 'NCC-1422', 'NCC-1017']

for data in dataList:
    # convert data to byte
    dataByte = data.encode()

    # create checksum
    values = (ACK, SEQ, dataByte)
    UDP_Data = struct.Struct('I I 8s')
    chkSum_Data = (UDP_Data.pack(*values))
    chkSum = bytes(hashlib.md5(chkSum_Data).hexdigest(), encoding="UTF-8")

    # make UDP packet to send to server
    values = (ACK, SEQ, dataByte, chkSum)
    UDP_Packet = UDP_Packet_Data.pack(*values)

    print("Sending Packet...")
    # set flag to true to run the while loop
    Flag = True
    while Flag == True:
        try:
            currentACK=ACK
            # send udp packet to server
            sock.sendto(UDP_Packet, (UDP_IP, UDP_Port))
            print("Packet Sent!\n")

            # wait for response from server
            responseSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # set the socket timeout to 9ms after that throw socket.timeout exception
            responseSocket.settimeout(0.009)
            responseSocket.bind((UDP_IP, 5004))

            print("Receiving Server Response...")

            # listen and get data from server
            rData, addr = responseSocket.recvfrom(1024)
            rPacket = clientUnpacker.unpack(rData)

            # compare data
            rACK = rPacket[0]
            if currentACK != rACK:
                # print packet data
                print("\nPrinting Server Response...")
                print(rPacket[0], rPacket[1], rPacket[2], "\n")
                print("Data Corrupted")
                #restart for loop
                continue
            else:
                # print packet data
                print("\nPrinting Server Response...")
                print(rPacket[0], rPacket[1], rPacket[2], "\n")
                print("Data not corrupted\n")
                correctRespSequence = rPacket[1]
                break

            # at the end set the while loop to false so it does resend the same packet
            Flag = False
        # if exception is raised set flag back to true and send the packet again
        except socket.timeout:
            Flag = True
            print("Server response timeout occurred... trying again\n")
            print("-----------------------------------------------------------------------------")
            continue

    # set the sequence again
    SEQ = correctRespSequence
    if ACK == 0:
        ACK = 1
    else:
        ACK = 0

    print("-----------------------------------------------------------------------------")

sock.close()
responseSocket.close()
