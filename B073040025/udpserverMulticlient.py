import socket
import struct
import threading
import time
from datetime import datetime
import tcppacket
from time import sleep
import dns.resolver

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

    s = struct.calcsize('!HHLLBBHHH')
    unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
    msg = (data[s:]).decode('utf-8')
    print(data[s:])
    print(unpackdata)
    while True:
        if(unpackdata[8] == 0):
            print("receive a text packet from client")
            print("content is : "+msg)
            reply = str("got text msg")
            fin_falg = 1

        elif(unpackdata[8] == 1):
            print("receive a math packet from client")
            reply = str("result of "+msg+" is "+str(eval(msg)))
            fin_falg = 1

        elif(unpackdata[8] == 2):
            print("receive a video request packet from client.")

            target = "../"+str(msg)+".mp4"
            f = open(target, "rb")

            while True:

                reply = f.read(max_seg_size)
                if(reply == b''):
                    reply = ''
                    fin_falg = 1
                    break
                tcp = tcppacket.TCPPacket(data=reply)
                tcp.assemble_tcp_feilds()
                thread_sock.sendto(tcp.raw, client_address)

                data, client_address = thread_sock.recvfrom(512*1024)
                s = struct.calcsize('!HHLLBBHHH')
                ACKunpackdata = struct.unpack('!HHLLBBHHH', data[:s])
                # unpackdata[5] is tcp flags
                if(ACKunpackdata[5] / 2**4):
                    print("recive ACK from :", client_address)

        elif(unpackdata[8] == 3):
            print("receive a dns request packet from client.")
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8']
            result_IP = resolver.resolve(msg, 'A')[0].to_text()
            reply = ("IP of "+msg+" is "+str(result_IP))
            fin_falg = 1

        # reply will encode in below
        # send packet
        # print(fin_falg)
        tcp = tcppacket.TCPPacket(data=reply.encode('utf-8'),
                                  flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        thread_sock.sendto(tcp.raw, client_address)

        # receive AKC
        data, client_address = thread_sock.recvfrom(512*1024)
        s = struct.calcsize('!HHLLBBHHH')
        unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
        # unpackdata[5] is tcp flags
        if(unpackdata[5] / 2**4):
            print("recive ACK from :", client_address)

        # print(unpackdata)

        # print(thread_num_array)
        # if both fin and ack eq 1
        if(unpackdata[5] % 2 and unpackdata[5] / 2**4):
            thread_num_array[threadnum] = 0
            break

    pass
# -------------------------------------------------------
# -------------------------------------------------------
# -------------------------------------------------------


def shutdown_server():
    ''' Shutdown the UDP server '''
    printwt('Shutting down server...')
    sock.close()


''' Create a UDP Server and handle multiple clients simultaneously '''

printwt('Creating socket...')
printwt('Socket created')
# bind server to the address
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((host, port))    # Socket
printwt(f'Binding server to {host}:{port}...')
printwt(f'Server binded to {host}:{port}')
print(sock)
wait_for_client()