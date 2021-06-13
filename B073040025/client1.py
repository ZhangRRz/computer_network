import socket
import struct
import threading
import tcppacket
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


def create_new_client(i):
    global thread_lock_input_part
    while(thread_lock_input_part):
        pass
    thread_lock_input_part = 1
    videoreq = 0

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    PacketType = input('Input the PacketType you want to transmit: \n')
    if(PacketType == "text"):
        data = input("Input your text that want to send: \n")
        what_is_packet = 0
    elif(PacketType == "calc"):
        data = input("Input math expression: \n")
        what_is_packet = 1
    elif(PacketType == "video"):
        data = input("Input which video you want: \n")
        what_is_packet = 2
        videoreq = 1
    elif(PacketType == "dns"):
        data = input("Input which IP of domain name you want get: \n")
        what_is_packet = 3
    else:
        print("PacketType ERROR")
        thread_lock_input_part = 0
        return 0
    thread_lock_input_part = 0

    # Sending request to UDP server
    tcp = tcppacket.TCPPacket(data=data.encode(
        'utf-8'), what_is_packet=what_is_packet)
    tcp.assemble_tcp_feilds()
    print("request send to (IP,port):", udp_host, " , ", udp_port)
    sock.sendto(tcp.raw, (udp_host, udp_port))

    videodata = b''
    # receive packet
    while True:

        data, senderAddr = sock.recvfrom(512*1024)
        # bind client to target server thread port num
        sock.connect(senderAddr)

        s = struct.calcsize('!HHLLBBHHH')
        unpackdata = struct.unpack('!HHLLBBHHH', data[:s])

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

        tcp = tcppacket.TCPPacket(
            data=str("ACK").encode('utf-8'),
            flags_ack=1,
            flags_fin=fin_falg)
        tcp.assemble_tcp_feilds()
        print("ACK send to (IP,port):", senderAddr)
        sock.sendto(tcp.raw, senderAddr)

        if(fin_falg):
            if(videoreq):
                f = open("received.mp4", "wb")
                f.write(videodata)
                f.close()
            break


threads = []
for i in range(1):
    threads.append(threading.Thread(target=create_new_client, args=(i,)))
    threads[-1].start()

# for i in range(1):
#     threads.append(threading.Thread(
#         target=init_new_calc_client, args=(i,)))
#     threads[-1].start()
