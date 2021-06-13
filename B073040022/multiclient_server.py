import socket	# base module
from random import randint
import dns.resolver	# for ip query pip3 install dnspython
import threading
from datetime import datetime
import struct
from segment import Segment
import time
# socket.socket() will create a TCP socket (default)
# socket.socket(socket.AF_INET, socket.SOCK_STREAM) to explicitly define a TCP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # explicitly define a UDP socket
udp_host = socket.gethostbyname(socket.gethostname()) # host IP
udp_port = 12345    # specified port to connect
sock.bind((udp_host,udp_port))
# 1-1 set arguments
max_rtt = 15/1000	# sec
# in bytes
max_seg_size = 1024
threshold = 64*1024	# ssthresh
buffer_size = 512*1024
socket_lock = threading.Lock()
tcp_header_len = struct.calcsize('!HHLLBBHH')

def printwt(msg):
    ''' Print message with current time and date'''
    current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{current_date_time}] {msg}')

def sendto_client(msg,addr):
    with socket_lock:
        sock.sendto(msg, addr)

def handle_request(cmdln, addr):
    ''' Handle the client '''
    printwt(f'[ REQUEST from {addr} ]')
    cmd = cmdln.split('@')[0]
    ln = cmdln.split('@')[1]
    if cmd == 'video':
        filename='../'+ln
        file=open(filename,'rb')
        seq_num=randint(1,10000)
        while True:	# send until the whole file
            data=file.read(max_seg_size)
            sendto_client(data, addr)
            time.sleep(0.001)
            if data == b'':
                break
        file.close()
        print('video done!')
    elif cmd == 'math':
        form_list=ln.split(' ')
        if form_list[1] == '+':
            ans = float(form_list[0]) + float(form_list[2])
        elif form_list[1] == '-':
            ans = float(form_list[0]) - float(form_list[2])
        elif form_list[1] == '*':
            ans = float(form_list[0]) * float(form_list[2])
        elif form_list[1] == '/':
            ans = float(form_list[0]) / float(form_list[2])
        elif form_list[1] == '^':
            ans = float(form_list[0]) ** float(form_list[2])
        elif form_list[1] == 'sqrt':
            ans = float(form_list[0]) ** 0.5
        else:
            print('Error form, return -1')
            ans = -1
        msg = Segment(data=str(ans)).raw
        sendto_client(msg, addr)
        printwt(f'[ RESPONSE to {addr} ]')
    elif cmd == 'dns':
        resolver=dns.resolver.Resolver()
        resolver.nameservers=['8.8.8.8']
        msg = Segment(data=resolver.resolve(ln,'A')[0].to_text()).raw
        sendto_client(msg, addr)
        printwt(f'[ RESPONSE to {addr} ]')
    else:
        pass
    

# Wait for a client
try:
    while True: # keep alive
        try: # receive request from client
            print("Waitting for clients' command...")
            msg, client_addr = sock.recvfrom(buffer_size)
            header = struct.unpack('!HHLLBBHH', msg[:tcp_header_len])
            cmdln = msg[tcp_header_len:].decode('utf-8')
            c_thread = threading.Thread(target = handle_request, args = (cmdln, client_addr))
            c_thread.daemon = True
            c_thread.start()
        except OSError as err:
            printwt(err)
except KeyboardInterrupt:
    ''' Shutdown the UDP server '''
    print()
    printwt('Shutting down server...')
    sock.close()



