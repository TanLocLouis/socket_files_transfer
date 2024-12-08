from re import L
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
        # Request list of available resources
        message = "LIST\r\n"
        main_socket.sendto(message.encode(), (self.HOST, self.PORT))
        
        data, addr = main_socket.recvfrom(1024)
        data = data.decode()
        # Convert data to list
        list_file = eval(data)

        print(utils.setTextColor("green"), end="")
        print(f"[RESPONE] List of available resources:")
        print(utils.setTextColor("white"), end="")
        for file in list_file:
            print(f"[LIST] |----------{file}----------|")
        print("Press Enter to continue...")
        input()
        



        
s1 = SocketClientUDP()
s1.connect_to_server("input.txt")
         