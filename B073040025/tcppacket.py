import socket
import struct


class TCPPacket:
    def __init__(self,  sport=65535, dport=80, dst='127.0.0.1', src='192.168.1.101',
                 seq=0, ack_seq=0,
                 data=b'Nothing',
                 flags_ack=0, flags_psh=0,
                 flags_rst=0, flags_syn=0, flags_fin=0,
                 what_is_packet=0,
                 chksum=0
                 ):
        self.raw = None

        self.tcp_dst = dport
        self.tcp_src = sport
        # ---- [ TCP Sequence Number]
        self.tcp_seq = seq
        # ---- [ TCP Acknowledgement Number]
        self.tcp_ack_seq = ack_seq
        # ---- [ Header Length ]
        self.tcp_hdr_len = struct.calcsize('!HHLLBBHHH')
        # ---- [ TCP Window Size ]
        self.tcp_wdw = socket.htons(5840)
        # ---- [ TCP CheckSum ]
        self.tcp_chksum = chksum

        self.src_ip = src
        self.dst_ip = dst
        self.data = data
        self.what_is_packet = what_is_packet
        # ---- [ TCP Flags ]
        self.tcp_flags = (flags_ack << 4)\
            + (flags_psh << 3)\
            + (flags_rst << 2)\
            + (flags_syn << 1)\
            + (flags_fin)
        # print(self.tcp_flags)

    def assemble_tcp_feilds(self):
        self.raw = struct.pack('!HHLLBBHHH',  # Data Structure Representation
                               self.tcp_src,   # Source IP
                               self.tcp_dst,    # Destination IP
                               self.tcp_seq,    # Sequence
                               self.tcp_ack_seq,  # Acknownlegment Sequence
                               self.tcp_hdr_len,   # Header Length
                               self.tcp_flags,    # TCP Flags
                               self.tcp_wdw,   # TCP Windows
                               self.tcp_chksum,  # TCP cheksum
                               #    self.tcp_urg_ptr,  # TCP Urgent Pointer
                               self.what_is_packet  # to show packet is for what function
                               )
        self.raw = self.raw + self.data
        # self.calculate_chksum()  # Call Calculate CheckSum
        return
