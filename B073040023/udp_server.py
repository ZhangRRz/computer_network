from datetime import datetime
import socket
import time

class UDPServer:
    ''' A simple UDP Server '''
    def __init__(self, host, port):

        self.host = socket.gethostname()    # Host address
        self.port = 12345    # Host port
        self.sock = None    # Socket
    def printwt(self, msg):

        ''' Print message with current date and time '''
        current_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'[{current_date_time}] {msg}')
    def configure_server(self):


        ''' Configure the server '''
        # create UDP socket with IPv4 addressing

        self.printwt('Creating socket...')
        self.printwt('Socket created')
        # bind server to the address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.printwt(f'Binding server to {self.host}:{self.port}...')
        self.printwt(f'Server binded to {self.host}:{self.port}')

    def wait_for_client(self):

        ''' Wait for a client '''
        try:
            # receive message from a client

            data, client_address = self.sock.recvfrom(1024)
            print(data)
            # handle client's request

            self.handle_request(data, client_address)
        except OSError as err:
            self.printwt(err)
    def shutdown_server(self):


        ''' Shutdown the UDP server '''
        self.printwt('Shutting down server...')
        self.sock.close()