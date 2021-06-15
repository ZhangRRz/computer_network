import socket
import struct
import threading
import tcppacket
import random

# socket.socket() will create a TCP socket (default)
# socket.socket(socket.AF_INET, socket.SOCK_STREAM) to explicitly define a TCP socket
# explicitly define a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

udp_host = socket.gethostname()  # Host IP
udp_port = 12345    # specified port to connect

max_rtt = 15/1000  # sec
# in bytes
buffer_size = 512*1024

thread_lock_input_part = 0


def create_new_client(c_num):
    global thread_lock_input_part
    while(thread_lock_input_part):
        pass
    thread_lock_input_part = 1
    ack_seq = 0
    seq = seq = random.randint(1,10000)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    job = 'y'
    job_count = 0
    job_type = []
    data = ''

    while job == 'y':
        PacketType = input('Input the job you want to do: \n')
        job_count += 1
        if(PacketType == "calc"):
            data += PacketType+"\n"
            data += input("Input math expression: \n")
            job_type.append("calc")

        elif(PacketType == "video"):
            data += PacketType+"\n"
            data += input("Input which video you want: \n")
            job_type.append("video")
        
        elif(PacketType == "dns"):
            data += PacketType+"\n"
            data += input("Input which IP of domain name you want get: \n")
            job_type.append("dns")
        else:
            job_count -= 1
            print("PacketType ERROR")
        job = input("is there any job you want to do?(y/n)")
        if(job == 'y'):
            data += "\n"
    thread_lock_input_part = 0

    # Sending request to UDP server
    tcp = tcppacket.TCPPacket(data=data.encode('utf-8'),
                              seq=seq,
                              ack_seq=ack_seq)
    tcp.assemble_tcp_feilds()
    print("request send to (IP,port):", udp_host, " , ", udp_port)
    sock.sendto(tcp.raw, (udp_host, udp_port))
    seq += 1

    data, senderAddr = sock.recvfrom(512*1024)
    sock.connect(senderAddr)
    ack_seq = 1+(struct.unpack('!HHLLBBHHH', data[:struct.calcsize('!HHLLBBHHH')]))[2]

    videodata = b''

    recv_packet_count =0
    # receive packet
    for i in range(job_count):
        print("===============================================")
        if(job_type[i] == "video"):
            videoreq = 1
        else:
            videoreq = 0
        while True:

            data, senderAddr = sock.recvfrom(512*1024)
            # bind client to target server thread port num
            recv_packet_count += 1

            s = struct.calcsize('!HHLLBBHHH')
            unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
            print("receive packet from ", senderAddr,
                "with seq", unpackdata[2])

            # unpackdata[2] = tcp_seq
            # unpackdata[2] = checksum
            # only accept packet come in order and checksum is right
            if(unpackdata[2] == ack_seq and unpackdata[7] == 0):
                # current is right so ack for next one
                pass
            else:
                print("but the packet from ", senderAddr,
                    "with WRONG checksum",
                    " ack seq: ", unpackdata[3], " and seq: ", unpackdata[2])
            ack_seq += 1


            if(videoreq):
                    videodata += data[s:]
            else:
                recvmsg = data[s:].decode('utf-8')
                print("client ", c_num, " accept packet from server " +
                        str(senderAddr)+" :\n", recvmsg)
            # print(unpackdata)

            if(unpackdata[5] % 2):
                # fin_falg
                fin_falg = 1
            else:
                fin_falg = 0
            # --------------------------------------------
            # send ACK
            if(recv_packet_count == 3 or fin_falg == 1):
                recv_packet_count = 0

                chksum = maybe_make_packet_error()
                tcp = tcppacket.TCPPacket(
                    data=str("ACK").encode('utf-8'),
                    seq=seq, ack_seq=ack_seq,
                    flags_ack=1,
                    flags_fin=fin_falg,
                    chksum = chksum)
                tcp.assemble_tcp_feilds()
                print("ACK send to (IP,port):", senderAddr,
                    "with ack seq: ", ack_seq, " and seq: ", seq)
                sock.sendto(tcp.raw, senderAddr)
                seq += 1
            # --------------------------------------------

            if(fin_falg):
                if(videoreq):
                    savev = str(c_num)+"received.mp4"
                    f = open(savev, "wb")
                    f.write(videodata)
                    f.close()
                break


threads = []
for i in range(1):
    threads.append(threading.Thread(target=create_new_client, args=(i,)))
    threads[-1].start()

def maybe_make_packet_error():
    if(random.randint(1, 1000000) < 800000):
        # make packet error
        return 1
    return 0