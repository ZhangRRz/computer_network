import socket	# base module
from segment import Segment # my TCP packet structure
import struct   # for data unpacking
import threading    # for multiclient
from random import randint
# socket.socket() will create a TCP socket (default)
# socket.socket(socket.AF_INET, socket.SOCK_STREAM) to explicitly define a TCP socket
udp_host = socket.gethostbyname(socket.gethostname()) # host IP
udp_port = 12345    # specified port to connect
# 1-1 set arguments
max_rtt = 15/1000	# sec
# in bytes
max_seg_size = 1024
threshold = 64*1024	# ssthresh
buffer_size = 512*1024
tcp_header_len = struct.calcsize('!HHLLBBHHH')

def rand_chksum():
    '''set 25%'''
    return int(randint(1,1000000) > 750000)

def new_client(cmdlns:str):
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # explicitly define a UDP socket
    msg = Segment(data=cmdlns.encode('utf-8'), tcp_chksum=rand_chksum()).raw
    sock.sendto(msg, (udp_host,udp_port))
    try:
        for cmdln in cmdlns.split('|'):
            cmd = cmdln.split('@')[0]
            ln = cmdln.split('@')[1]
            if cmd == 'video':
                recv=b''
                delay_ack_counter=0
                while True:	# send until the whole file
                    data, addr = sock.recvfrom(buffer_size)
                    header = struct.unpack('!HHLLBBHHH', data[:tcp_header_len])
                    data = data[tcp_header_len:]
                    if header[6]:
                        print(f'[ CLIENT {sock.getsockname()} RECEIVE segment with packet loss ]')
                    else:
                        print(f'[ CLIENT {sock.getsockname()} RECEIVE segment ]')
                    recv+=data
                    delay_ack_counter+=1
                    if delay_ack_counter==3 or data == b'':
                        # send ack
                        msg = Segment(tcp_flags_ack=1, tcp_chksum=rand_chksum()).raw
                        sock.sendto(msg, addr)
                        print(f'[ CLIENT {sock.getsockname()} ACK to {addr} ]')                    
                        delay_ack_counter=0
                    if data == b'':
                        break
                prefix=addr[1]
                savename=str(prefix)+'_'+ln
                file=open(savename,'wb')
                file.write(recv)
                file.close()
                print(f'[ CLIENT {sock.getsockname()} RESPONSE from {addr} ] request for video: "{ln}" done!')
            elif cmd == 'math':
                ans, addr = sock.recvfrom(buffer_size)
                header = struct.unpack('!HHLLBBHHH', ans[:tcp_header_len])
                ans = ans[tcp_header_len:].decode('utf-8')
                if header[6]:
                    print(f'[ CLIENT {sock.getsockname()} RESPONSE from {addr} ] {ln} = {ans} with packet loss')
                else:
                    print(f'[ CLIENT {sock.getsockname()} RESPONSE from {addr} ] {ln} = {ans}')
                # send ack
                msg = Segment(tcp_flags_ack=1, tcp_chksum=rand_chksum()).raw
                sock.sendto(msg, addr)
                print(f'[ CLIENT {sock.getsockname()} ACK to {addr} ]')
            elif cmd == 'dns':
                ip, addr = sock.recvfrom(buffer_size)
                header = struct.unpack('!HHLLBBHHH', ip[:tcp_header_len])
                ip = ip[tcp_header_len:].decode('utf-8')
                if header[6]:
                    print(f'[ CLIENT {sock.getsockname()} RESPONSE from {addr} ] The IP address of "{ln}" is {ip} with packet loss')
                else:
                    print(f'[ CLIENT {sock.getsockname()} RESPONSE from {addr} ] The IP address of "{ln}" is {ip}')
                # send ack
                msg = Segment(tcp_flags_ack=1, tcp_chksum=rand_chksum()).raw
                sock.sendto(msg, addr)
                print(f'[ CLIENT {sock.getsockname()} ACK to {addr} ]')
            else:
                pass
    except KeyboardInterrupt:
        ''' Shutdown the UDP client '''
        print('\nShutting down client...')
        sock.close()

cmdlns_list=[]

##############################################
############### standard input ###############
##############################################
client_num=input('How many clients: ')
for i in range(int(client_num)):
    print('Input commands in the following form: cmdln{|cmdln}')
    print('video@filename')
    print('dns@domain_name')
    print('math@formula')
    print('\tA + B')
    print('\tA - B')
    print('\tA * B')
    print('\tA / B')
    print('\tA ** B')
    cmdlns = input('Input command: ')
    cmdlns_list.append(cmdlns)

#############################################
################# n clients #################
#############################################
# n=100
# for i in range(n):
#     cmdlns_list.append('video@1.mp4')


for cmdlns in cmdlns_list:
    client=threading.Thread(target=new_client, args=(cmdlns,))
    client.start()