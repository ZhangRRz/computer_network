import socket
from time import sleep
import threading
import dns.resolver
# socket.socket() will create a TCP socket (default)
# socket.socket(socket.AF_INET, socket.SOCK_STREAM) to explicitly define a TCP socket
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  # explicitly define a UDP socket

udp_host = 'TCat-Desktop' # Host IP
udp_port = 12345    # specified port to connect
buffer_size = 512*1024


def doCalc(msglist,addr):
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
	sock.sendto(bytes(str(ans),'ascii'),addr)

def sendVideo(msg,addr):
	videonumber = msg[-1]
	target = "../"+str(videonumber)+".mp4"
	f = open(target, "rb")
	seq_num = 10
	while True:
		data = f.read(1024)
		print(data)
		sock.sendto(data,addr)
		if(data == b''):
			break
	pass

def dns_req(msglist,addr):
	resolver = dns.resolver.Resolver()
	resolver.nameservers=['8.8.8.8']
	sock.sendto(bytes(resolver.resolve(msglist[1],'A')[0].to_text(),'ascii'),addr)
	print('done!')

sock.bind((udp_host,udp_port))
threads = []
while True:
	print("Waiting for client...")
	data, addr = sock.recvfrom(buffer_size)    # number of bytes to send = 512 KBytes
	msg = data.decode('utf-8')
	msglist = msg.split(' ')
	print("Received Messages:", msg, " from", addr)
	if(msglist[0] == "calc"):
		threads.append(threading.Thread(target = doCalc, args = (msglist,addr,)))
		threads[-1].start()
	elif(msglist[0] == "video"):
		threads.append(threading.Thread(target = sendVideo, args = (msglist,addr,)))
		threads[-1].start()
	elif(msglist[0] == "dns"):
		threads.append(threading.Thread(target = dns_req, args = (msglist,addr,)))
		threads[-1].start()