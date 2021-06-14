import socket
import threading
import tcppacket
import struct
from time import sleep

# socket.socket() will create a TCP socket (default)
# socket.socket(socket.AF_INET, socket.SOCK_STREAM) to explicitly define a TCP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # explicitly define a UDP socket

udp_host = '127.0.0.1' # Host IP
udp_port = 12345    # specified port to connect

def init_new_calc_req(msg):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    oldmsg = msg 
    msg = msg.encode('utf-8')
    tcp = tcppacket.TCPPacket(data=msg)
    tcp.assemble_tcp_feilds()
    sock.sendto(tcp.raw, (udp_host, udp_port)) 
    # print("UDP target IP:", udp_host)
    # print("UDP target Port:", udp_port)   # Sending message to UDP server
    while True:
        data, address = sock.recvfrom(512*1024) 
        sock.connect(address)

        s = struct.calcsize('!HHLLBBH')
        unpackdata = struct.unpack('!HHLLBBH', data[:s])

        msg = data[s:].decode('utf-8')
        print(oldmsg,"is", msg)
        if(unpackdata[5] % 2):
            # fin_falg
            fin_falg = 1
        else:
            fin_falg = 0

        tcp = tcppacket.TCPPacket(
            data="ACK".encode('utf-8'),
            flags_ack=1,
            flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        print("ACK send to (IP,port):", address)
        sock.sendto(tcp.raw, address)
        if(fin_falg):
            break

def init_new_videoreq_req(i):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    msg = str("video "+str(i+1)).encode('utf-8')
    # print("UDP target IP:", udp_host)
    # print("UDP target Port:", udp_port)
    tcp = tcppacket.TCPPacket(data=msg)
    tcp.assemble_tcp_feilds()
    sock.sendto(tcp.raw, (udp_host, udp_port))   # Sending message to UDP server
    recvdata = b''
    ack_seq = 0
    seq = 0
    counter = 0
    while True:
        data, address = sock.recvfrom(512*1024) 

        s = struct.calcsize('!HHLLBBHHH')
        raw = struct.unpack('!HHLLBBHHH', data[:s])
        print("receive packet from ", address)
        fin_flag = raw[5] % 2
        recvdata += data[s:]
        if(raw[2] == ack_seq and raw[7] == 0):
            if(fin_flag):
                break
        elif(raw[2] == ack_seq):
            print("Receive ERROR packet from ", address)
        ack_seq += 1
        counter += 1
        # --------------------------------------------
        # send ACK
        if(counter == 3 or fin_flag):
            tcp = tcppacket.TCPPacket(
                data=str("ACK").encode('utf-8'),
                seq=seq, ack_seq=ack_seq,
                flags_ack=1,
                flags_fin=fin_flag)
            tcp.assemble_tcp_feilds()
            print("ACK send to (IP,port):", address,"with ack seq:", ack_seq)
            sock.sendto(tcp.raw, address)
            if(not fin_flag):
                counter = 0
        seq += 1
        # --------------------------------------------
        if(fin_flag):
            break
    savename = str(i+1)+"received.mp4"
    f = open(savename, "wb")
    f.write(recvdata)
    f.close()

def init_new_dns_req(i):
    # ---------------------
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    oldmsg = msg = "dns google.com"
    msg = msg.encode('utf-8')
    tcp = tcppacket.TCPPacket(data=msg)
    tcp.assemble_tcp_feilds()
    sock.sendto(tcp.raw, (udp_host, udp_port)) 
    # print("UDP target IP:", udp_host)
    # print("UDP target Port:", udp_port)
    while True:
        data, address = sock.recvfrom(512*1024) 
        sock.connect(address)

        s = struct.calcsize('!HHLLBBH')
        unpackdata = struct.unpack('!HHLLBBH', data[:s])

        msg = data[s:].decode('utf-8')
        print(oldmsg,"is", msg)
        if(unpackdata[5] % 2):
            # fin_falg
            fin_falg = 1
        else:
            fin_falg = 0

        tcp = tcppacket.TCPPacket(
            data="ACK".encode('utf-8'),
            flags_ack=1,
            flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        print("ACK send to (IP,port):", address)
        sock.sendto(tcp.raw, address)
        if(fin_falg):
            break
    # ----------------------
    
def init_oneRQ_multiCommand():
    x = input("type the number of commands:")
    # "3 calc 1+1 | video 1 | dns google.com"
    msg = ""
    msg += str(x)
    msg += " "
    for i in range(x):
        tmp = input("Input command #"+str(i+1)+":")
        msg += str(tmp)
        msg += " "
    print(msg)
    exit()
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    msg = msg.encode('utf-8')
    tcp = tcppacket.TCPPacket(data=msg)
    tcp.assemble_tcp_feilds()
    sock.sendto(tcp.raw, (udp_host, udp_port)) 
    while True:
        data, address = sock.recvfrom(512*1024) 
        sock.connect(address)

        s = struct.calcsize('!HHLLBBH')
        unpackdata = struct.unpack('!HHLLBBH', data[:s])

        msg = data[s:].decode('utf-8')
        print(oldmsg,"is", msg)
        if(unpackdata[5] % 2):
            # fin_falg
            fin_falg = 1
        else:
            fin_falg = 0

        tcp = tcppacket.TCPPacket(
            data="ACK".encode('utf-8'),
            flags_ack=1,
            flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        print("ACK send to (IP,port):", address)
        sock.sendto(tcp.raw, address)
        if(fin_falg):
            break

threads = []
# Calculation--------------------------------------
print("Demo calculation function")
init_new_calc_req("calc (5+5)-(10*10)+(30/6)+2**4-4**0.5")
print("-"*60)
print("Demo DNS request function")
for i in range(3):
    threads.append(threading.Thread(target = init_new_dns_req, args = (i,)))
    threads[-1].start()
init_oneRQ_multiCommand()
# for i in range(2):
#     threads.append(threading.Thread(target = init_new_videoreq_req, args = (i,)))
#     threads[-1].start()