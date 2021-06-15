import socket
import struct
import threading
import time
from datetime import datetime
import tcppacket
from time import sleep
import dns.resolver
import random

''' A simple UDP Server for handling multiple clients '''
max_seg_size = 1024
threshold = 64*1024  # ssthresh

socket_lock = threading.Lock()
host = str(socket.gethostname())  # Host address
port = 12345    # Host port


def printwt(msg):
    ''' Print message with current date and time '''
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] {msg}')


thread_num_array = [0, 0, 0, 0, 0]


def find_avalible_thread_num():
    for i in range(5):
        if (not thread_num_array[i]):
            thread_num_array[i] = 1
            return i
    return -1


def wait_for_client():
    ''' Wait for clients and handle their requests '''
    try:
        while True:  # keep alive

            try:  # receive request from client
                print("Waiting for client...")
                data, client_address = sock.recvfrom(512*1024)
                print("Received!")

                threadnum = find_avalible_thread_num()
                while (threadnum == -1):
                    threadnum = find_avalible_thread_num()
                    # loop here till find avalible threadnum
                    print("wait for avalible threadnum...")
                    sleep(1)
                    pass
                c_thread = threading.Thread(target=handle_request,
                                            args=(data, client_address, threadnum))
                c_thread.daemon = True
                c_thread.start()

            except OSError as err:
                printwt(err)

    except KeyboardInterrupt:
        shutdown_server()
# -------------------------------------------------------
# handle_request
# -------------------------------------------------------


def handle_request(data, client_address, threadnum):
    ''' Handle the client '''
    thread_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    thread_sock.bind((host, port+threadnum+1))

    # ----------------------------------------------
    # slove client request
    s = struct.calcsize('!HHLLBBHHH')
    unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
    command_and_data = (data[s:]).decode('utf-8').split('\n')
    print(command_and_data)
    # ----------------------------------------------
    command = ''
    msg = ''
    ack_seq = unpackdata[2]+1
    seq = random.randint(1,10000)
    # ----------------------------------------------
    # ack client request
    req_ack = tcppacket.TCPPacket(
                    data=str("ACK from server").encode('utf-8'),
                    seq=seq, ack_seq=ack_seq,
                    flags_ack=1)
    req_ack.assemble_tcp_feilds()
    thread_sock.sendto(req_ack.raw, client_address)
    seq += 1
    # ----------------------------------------------

    # start handle context of request
    for i in range(int(len(command_and_data)/2)):
        print("===============================================")
        command = command_and_data[2*i]
        msg = command_and_data[2*i+1]

        if(command == "calc"):
            print("dealing with math claculation ")
            reply = str("result of "+msg+" is "+str(eval(msg))).encode('utf-8')
            fin_falg = 1

        elif(command == "video"):
            print("dealing with video request ")
            target = "../"+str(msg)+".mp4"
            f = open(target, "rb")

        elif(command == "dns"):
            print("dealing with dns request ")
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8']
            result_IP = resolver.resolve(msg, 'A')[0].to_text()
            reply = ("IP of "+msg+" is "+str(result_IP)).encode('utf-8')
            fin_falg = 1

        send_packet_count = 0
        while True:
            # if video requset reply will make at here
            if(command == "video"):
                reply = f.read(max_seg_size)
                fin_falg = 0
                if(reply == b''):
                    fin_falg = 1

            # -------------------------------------------------------
            # reply will encode in below and make a packet for sending
            # -------------------------------------------------------
            chksum = maybe_make_packet_error()
            tcp = tcppacket.TCPPacket(data=reply,
                                    seq=seq, ack_seq=ack_seq,
                                    flags_fin=fin_falg,
                                    chksum=chksum)
            tcp.assemble_tcp_feilds()
            thread_sock.sendto(tcp.raw, client_address)
            print("send a packet to ", client_address,
                "with server seq :", seq)
            seq += 1
            send_packet_count += 1

            # receive ACK
            if(send_packet_count == 3 or fin_falg == 1):
                send_packet_count = 0

                data, client_address = thread_sock.recvfrom(512*1024)
                s = struct.calcsize('!HHLLBBHHH')
                unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
                # unpackdata[5] is tcp flags
                if(unpackdata[5] / 2**4):
                    print("recive ACK from :", client_address,
                        "with ack seq: ", unpackdata[3], " and client seq: ", unpackdata[2])
                if(unpackdata[7] == 0):
                    # current is right so ack for next one
                    pass
                else:
                    print("but the packet from ", client_address,
                        "with WRONG checksum",
                        " ack seq: ", unpackdata[3], " and seq: ", unpackdata[2])
                ack_seq += 1

            if(unpackdata[5] % 2 and unpackdata[5] / 2**4):
                thread_num_array[threadnum] = 0
                break

    pass
# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------


def maybe_make_packet_error():
    if(random.randint(1, 1000000) < 800000):
        # make packet error
        return 1
    return 0


def shutdown_server():
    # Shutdown the UDP server 
    printwt('Shutting down server...')
    sock.close()

# -------------------------------------------------------
# Create a UDP Server and handle multiple clients simultaneously
# -------------------------------------------------------
printwt('Creating socket...')
printwt('Socket created')
# bind server to the address
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))    # Socket
printwt(f'Binding server to {host}:{port}...')
printwt(f'Server binded to {host}:{port}')
print(sock)
wait_for_client()
