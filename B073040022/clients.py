import socket	# base module
import time
from segment import Segment
import struct
# socket.socket() will create a TCP socket (default)
# socket.socket(socket.AF_INET, socket.SOCK_STREAM) to explicitly define a TCP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # explicitly define a UDP socket
udp_host = socket.gethostbyname(socket.gethostname()) # host IP
udp_port = 12345    # specified port to connect
# 1-1 set arguments
max_rtt = 15/1000	# sec
# in bytes
max_seg_size = 1024
threshold = 64*1024	# ssthresh
buffer_size = 512*1024
tcp_header_len = struct.calcsize('!HHLLBBHH')

# test
def test_rtt():
    init_time = time.time()
    sock.sendto(bytes('test rtt','utf-8'), (udp_host,udp_port))
    data, addr = sock.recvfrom(buffer_size)
    # print("Received Messages:", data.decode('utf-8'), " from", addr)
    if data.decode('utf-8') == 'return rtt':
        end_time = time.time()-init_time
        print('The Round Trip Time is {}'.format(end_time))

try:
    while(True):
        print('Input command in the following form:')
        print('video@filename')
        print('math@formula')
        # print('A + B')
        # print('A - B')
        # print('A * B')
        # print('A / B')
        # print('A ^ B')
        # print('A sqrt')
        print('dns@domain_name')
        cmdln = input('Input command: ')
        cmd = cmdln.split('@')[0]
        ln = cmdln.split('@')[1]
        msg = Segment(data=cmdln).raw
        sock.sendto(msg, (udp_host,udp_port))
        if cmd == 'video':
            recv=b''
            while True:	# send until the whole file
                data, addr = sock.recvfrom(buffer_size)
                recv+=data
                if data == b'':
                    break
            savename='saved_'+ln
            file=open(savename,'wb')
            file.write(recv)
            file.close()
            print('video done!')
            time.sleep(3)   # wait to enter next loop
        elif cmd == 'math':
            ans, addr = sock.recvfrom(buffer_size)
            header = struct.unpack('!HHLLBBHH', ans[:tcp_header_len])
            ans = ans[tcp_header_len:].decode('utf-8')
            print('{} = {}'.format(ln, ans))
            time.sleep(3)   # wait to enter next loop
        elif cmd == 'dns':
            ip, addr = sock.recvfrom(buffer_size)
            header = struct.unpack('!HHLLBBHH', ip[:tcp_header_len])
            ip = ip[tcp_header_len:].decode('utf-8')
            print('The IP address of "{}" is {}'.format(ln,ip))
            time.sleep(3)   # wait to enter next loop
        else:
            pass
except KeyboardInterrupt:
    ''' Shutdown the UDP client '''
    print('\nShutting down client...')
    sock.close()