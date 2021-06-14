import socket
import threading
import tcppacket
import struct
# socket.socket() will create a TCP socket (default)
# socket.socket(socket.AF_INET, socket.SOCK_STREAM) to explicitly define a TCP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # explicitly define a UDP socket

udp_host = '127.0.0.1' # Host IP
udp_port = 12345    # specified port to connect

def init_new_calc_req(i):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    oldmsg = msg = "calc 2 ^ 10"
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
            data="ACK",
            flags_ack=1,
            flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        print("ACK send to (IP,port):", address)
        sock.sendto(tcp.raw, address)
        if(fin_falg):
            break

def init_new_videoreq_req(i):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    msg = "video 1"
    # print("UDP target IP:", udp_host)
    # print("UDP target Port:", udp_port)
    tcp = tcppacket.TCPPacket(data=msg)
    tcp.assemble_tcp_feilds()
    sock.sendto(tcp.raw, (udp_host, udp_port))   # Sending message to UDP server
    recvdata = b''
    ack_seq = 0
    seq = 0
    if(unpackdata[2] == ack_seq and unpackdata[7] == 0):

            if(videoreq):
                videodata += data[s:]
            else:
                recvmsg = data[s:].decode('utf-8')
                print("client ", i, " accept packet from server " +
                      str(senderAddr)+" :\n", recvmsg)
            # print(unpackdata)

            if(unpackdata[5] % 2):
                # fin_falg
                fin_falg = 1
            else:
                fin_falg = 0

            # current is right so ack for next one
            ack_seq += 1
        else:
            print("receive packet from ", senderAddr,
                  "with WRONG header", unpackdata)
            fin_falg = 0
        # --------------------------------------------
        # send ACK
        tcp = tcppacket.TCPPacket(
            data=str("ACK").encode('utf-8'),
            seq=seq, ack_seq=ack_seq,
            flags_ack=1,
            flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        print("ACK send to (IP,port):", senderAddr,
              "with ack seq: ", ack_seq, " and seq: ", seq)
        sock.sendto(tcp.raw, senderAddr)
        seq += 1
        # --------------------------------------------

        if(fin_falg):
            if(videoreq):
                f = open("received.mp4", "wb")
                f.write(videodata)
                f.close()
            break

def init_new_dns_req(i):
    # ---------------------
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    oldmsg = msg = "dns google.com"
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
            data="ACK",
            flags_ack=1,
            flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        print("ACK send to (IP,port):", address)
        sock.sendto(tcp.raw, address)
        if(fin_falg):
            break
    # ----------------------
    

threads = []
# for i in range(500):
#     threads.append(threading.Thread(target = init_new_calc_req, args = (i,)))
    # threads[-1].start()

for i in range(100):
    threads.append(threading.Thread(target = init_new_dns_req, args = (i,)))
    threads[-1].start()

# for i in range(1):
#     threads.append(threading.Thread(target = init_new_videoreq_req, args = (i,)))
#     threads[-1].start()