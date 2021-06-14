import socket,struct
import threading
import time
from datetime import datetime
import dns.resolver
import tcppacket,random

class UDPServerMultiClient():
    ''' A simple UDP Server for handling multiple clients '''

    def __init__(self, host, port):
        self.socket_lock = threading.Lock()
        self.host = host  # Host address
        self.port = port    # Host port
        self.sock = None    # Socket

    def dns_req(self,msglist,addr,temp_sock):
        resolver = dns.resolver.Resolver()
        resolver.nameservers=['8.8.8.8']
        msg = resolver.resolve(msglist[1],'A')[0].to_text().encode('utf-8')
        # self.sock.sendto(bytes(resolver.resolve(msglist[1],'A')[0].to_text(),'ascii'),addr)
        # print('done!')
        while True:
            fin_flag = 1
            tcp = tcppacket.TCPPacket(data=msg, flags_fin=fin_flag)
            tcp.assemble_tcp_feilds()
            temp_sock.sendto(tcp.raw, addr) 

            #--------------ACK---------------
            print("Waiting for ACK")
            data, client_address = temp_sock.recvfrom(512*1024)
            s = struct.calcsize('!HHLLBBHHH')
            unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
            if(unpackdata[5] / 2**4):
                print("recive ACK from :", client_address)
            if(unpackdata[5] % 2 and unpackdata[5] / 2**4):
                break

    def doCalc(self,msglist,addr,temp_sock):
        print("calculating...",addr)
        if msglist[2] == '+':
            ans = float(msglist[1]) + float(msglist[3])
        elif msglist[2] == '-':
            ans = float(msglist[1]) - float(msglist[3])
        elif msglist[2] == '*':
            ans = float(msglist[1]) * float(msglist[3])
        elif msglist[2] == '/':
            ans = float(msglist[1]) / float(msglist[3])
        elif msglist[2] == '^':
            ans = float(msglist[1]) ** float(msglist[3])
        elif msglist[2] == 'sqrt':
            ans = float(msglist[1]) ** 0.5
        else:
            print('Error form, return -1')
            ans = -1
        msg = str(ans).encode('utf-8')
        while True:
            fin_flag = 1
            tcp = tcppacket.TCPPacket(data=msg, flags_fin=fin_flag)
            tcp.assemble_tcp_feilds()
            temp_sock.sendto(tcp.raw, addr) 

            #--------------ACK---------------
            print("Waiting for ACK")
            data, client_address = temp_sock.recvfrom(512*1024)
            s = struct.calcsize('!HHLLBBHHH')
            unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
            if(unpackdata[5] / 2**4):
                print("recive ACK from :", client_address)
            if(unpackdata[5] % 2 and unpackdata[5] / 2**4):
                break

    def sendVideo(self,msg,addr,temp_sock):
        videonumber = msg[-1]
        target = "../"+str(videonumber)+".mp4"
        f = open(target, "rb")
        # seq_num = 10
        ack_seq = 0
        seq = 0
        pendingSendData = b''
        chksum = 0
        counter = 0
        while True:
            pendingSendData = f.read(1024)
            if(pendingSendData == b''):
                pendingSendData = ''
                fin_flag = 1
                break
            chksum = maybe_make_packet_error()
            tcp = tcppacket.TCPPacket(data=pendingSendData,
                                        seq=seq, ack_seq=ack_seq,chksum=chksum)
            tcp.assemble_tcp_feilds()
            temp_sock.sendto(tcp.raw, addr)
            print("send a packet to ", addr,
                    "with server seq :", seq)
            seq += 1
            counter += 1
            #-----------Delay ACK with counter
            if(counter == 3):
                data, addr = temp_sock.recvfrom(512*1024)
                s = struct.calcsize('!HHLLBBHHH')
                unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
                if(unpackdata[5] / 2**4):
                    print("recive ACK from :", addr,\
                    "with ack seq: ", unpackdata[3], " and client seq: ", unpackdata[2])
                counter = 0

        chksum = maybe_make_packet_error()
        tcp = tcppacket.TCPPacket(data=pendingSendData.encode('utf-8'),
                                  seq=seq, ack_seq=ack_seq,
                                  flags_fin=fin_flag,
                                  chksum=chksum)
        tcp.assemble_tcp_feilds()
        temp_sock.sendto(tcp.raw, addr)
        print("send a packet to ", addr,
              "with server seq :", seq)
        seq += 1

        # receive ACK
        data, addr = temp_sock.recvfrom(512*1024)
        s = struct.calcsize('!HHLLBBHHH')
        unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
        # unpackdata[5] is tcp flags
        if(unpackdata[5] / 2**4):
            print("recive ACK from :", addr,
                  "with ack seq: ", unpackdata[3], " and client seq: ", unpackdata[2])
        pass

    def configure_server(self):


        ''' Configure the server '''
        # create UDP socket with IPv4 addressing

        self.printwt('Creating socket...')
        self.printwt('Socket created')
        # bind server to the address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host,self.port))
        self.printwt(f'Binding server to {self.host}:{self.port}...')
        self.printwt(f'Server binded to {self.host}:{self.port}')

    def handle_request(self, msglist, client_address):
        ''' Handle the client '''
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if(msglist[0].find("calc") != -1):
            self.doCalc(msglist,client_address,temp_sock)
        elif(msglist[0].find("video") != -1):
            self.sendVideo(msglist,client_address,temp_sock)
        elif(msglist[0].find("dns") != -1):
            self.dns_req(msglist,client_address,temp_sock)
        pass

    def printwt(self, msg):

        ''' Print message with current date and time '''
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_date_time}] {msg}')

    def wait_for_client(self):
        ''' Wait for clients and handle their requests '''
        try:
            while True: # keep alive

                try: # receive request from client
                    print("Waiting for client...")
                    data, client_address = self.sock.recvfrom(1024)
                    print("Received request from client:",client_address)

                    s = struct.calcsize('!HHLLBBH')
                    unpackdata = struct.unpack('!HHLLBBH', data[:s])
                    msg = data[s:].decode('utf-8')
                    if(not isinstance(msg[0], int)):
                        msglist = msg.split(' ')
                        c_thread = threading.Thread(target = self.handle_request,
                                                args = (msglist, client_address))
                        c_thread.daemon = True
                        c_thread.start()
                    else:
                        index = msg.find("***")
                        msglist1 = msg[:index].split(' ')
                        msglist2 = msg[index+3:index].split(' ')
                        print(msglist1,msglist2)
                        exit()


                except OSError as err:
                    self.printwt(err)

        except KeyboardInterrupt:
            self.shutdown_server()
    
    def shutdown_server(self):


        ''' Shutdown the UDP server '''
        self.printwt('Shutting down server...')
        self.sock.close()

def maybe_make_packet_error():
    if(random.randint(1, 1000000) < 1000000):
        # make packet error
        return 1
    return 0

def main():
    ''' Create a UDP Server and handle multiple clients simultaneously '''

    udp_server_multi_client = UDPServerMultiClient('127.0.0.1', 12345)
    udp_server_multi_client.configure_server()
    udp_server_multi_client.wait_for_client()

if __name__ == '__main__':
    main()