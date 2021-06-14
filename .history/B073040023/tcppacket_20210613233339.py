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

    # def reassemble_tcp_feilds(self):
    #     self.raw = struct.pack('!HHLLBBH',
    #                            self.tcp_src,
    #                            self.tcp_dst,
    #                            self.tcp_seq,
    #                            self.tcp_ack_seq,
    #                            self.tcp_hdr_len,
    #                            self.tcp_flags,
    #                            self.tcp_wdw
    #                            )
    #     # +struct.pack("H", self.tcp_chksum)
    #     # +struct.pack('!H', self.tcp_urg_ptr)
    #     self.raw = self.raw + self.data.encode('utf-8')
    #     return

    # def calculate_chksum(self):
    #     src_addr = socket.inet_aton(self.src_ip)
    #     dest_addr = socket.inet_aton(self.dst_ip)
    #     placeholder = 0
    #     protocol = socket.IPPROTO_TCP
    #     tcp_len = len(self.raw) + len(self.data)

    #     psh = struct.pack('!4s4sBBH',
    #                       src_addr,
    #                       dest_addr,
    #                       placeholder,
    #                       protocol,
    #                       tcp_len
    #                       )

    #     psh = psh + self.raw + self.data.encode('utf-8')

    #     self.tcp_chksum = self.chksum(psh)

    #     self.reassemble_tcp_feilds()

    #     return

    # def chksum(self, msg):
    #     s = 0  # Binary Sum

    #     # loop taking 2 characters at a time
    #     for i in range(0, len(msg), 2):

    #         a = ord(msg[i])
    #         b = ord(msg[i+1])
    #         s = s + (a+(b << 8))

    #     # One's Complement
    #     s = s + (s >> 16)
    #     s = ~s & 0xffff
    #     return s

    # def create_tcp_feilds(self):

    #     # ---- [ Header Length ]
    #     self.tcp_hdr_len = 80

    #     # ---- [ TCP Window Size ]
    #     self.tcp_wdw = socket.htons(5840)

    #     # ---- [ TCP CheckSum ]
    #     self.tcp_chksum = 0

    #     # ---- [ TCP Urgent Pointer ]
    #     self.tcp_urg_ptr = 0

    #     return
