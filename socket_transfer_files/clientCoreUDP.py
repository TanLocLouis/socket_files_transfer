import socket
import time
import math
import utils
import threading
import os

class SocketClientUDP:
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 6969
    INPUT_UPDATE_INTERVAL = 5
    PIPES = 4
    METADATA_SIZE = 1024

    CHUNK_SIZE = 1048576  # 1 MB
    HEADER_SIZE = 8
    DELIMETER_SIZE = 2  # for \r\n
    MESSAGE_SIZE = 256

    def connect_to_server(self, filename):
        """
        Connect to the server and send the request to download the file.
        """
        
        # self.HOST = server_ip
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.handle_server_connection(main_socket)
        finally:
            # Close the socket
            main_socket.close()
           
    def handle_server_connection(self, main_socket):
        main_socket.sendto(b"Hello from client", (self.HOST, self.PORT))
        
s1 = SocketClientUDP()
s1.connect_to_server("input.txt")
         