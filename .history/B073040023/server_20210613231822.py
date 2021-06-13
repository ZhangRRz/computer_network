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

    def dns_req(self,msglist,addr):
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        resolver = dns.resolver.Resolver()
        resolver.nameservers=['8.8.8.8']
        msg = resolver.resolve(msglist[1],'A')[0].to_text()
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

    def doCalc(self,msglist,addr):
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        msg = str(ans)
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

    def sendVideo(self,msg,addr):
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        videonumber = msg[-1]
        target = "../"+str(videonumber)+".mp4"
        f = open(target, "rb")
        seq_num = 10
        ack_seq = 0
        seq = 0
        while True:
            data = f.read(1024)
            if(data == b''):
                reply = ''
                fin_falg = 1
                break
            tcp = tcppacket.TCPPacket(data=reply,
                                        seq=seq, ack_seq=ack_seq)
            tcp.assemble_tcp_feilds()
            temp_sock.sendto(tcp.raw, addr)
            print("send a packet to ", addr,
                    "with server seq :", seq)
            seq += 1

            data, client_address = temp_sock.recvfrom(512*1024)
            s = struct.calcsize('!HHLLBBHHH')
            unpackdata = struct.unpack('!HHLLBBHHH', data[:s])
            # unpackdata[5] is tcp flags
            if(unpackdata[5] / 2**4):
                print("recive ACK from :", client_address,
                        "with ack seq: ", unpackdata[3], " and client seq: ", unpackdata[2])
            if(unpackdata[3] == seq):
                # ack in correct order
                pass
            elif(unpackdata[3] == seq-1):
                seq = unpackdata[3]
                tcp = tcppacket.TCPPacket(data=reply,
                                            seq=seq, ack_seq=ack_seq)
                tcp.assemble_tcp_feilds()
                temp_sock.sendto(tcp.raw, client_address)
                seq += 1
            else:
                print("order error catch")
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

    def handle_request(self, data, client_address):
        ''' Handle the client '''
        s = struct.calcsize('!HHLLBBH')
        unpackdata = struct.unpack('!HHLLBBH', data[:s])
        msg = data[s:].decode('utf-8')
        msglist = msg.split(' ')
        if(msglist[0].find("calc") != -1):
            self.doCalc(msglist,client_address)
        elif(msglist[0].find("video") != -1):
            self.sendVideo(msglist,client_address)
        elif(msglist[0].find("dns") != -1):
            self.dns_req(msglist,client_address)
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
                    c_thread = threading.Thread(target = self.handle_request,
                                            args = (data, client_address))
                    c_thread.daemon = True
                    c_thread.start()

                except OSError as err:
                    self.printwt(err)

        except KeyboardInterrupt:
            self.shutdown_server()
    
    def shutdown_server(self):


        ''' Shutdown the UDP server '''
        self.printwt('Shutting down server...')
        self.sock.close()


def maybe_make_packet_error():
    if(random.randint(1, 1000000) < 750000):
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