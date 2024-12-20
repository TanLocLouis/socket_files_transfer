import socket
from turtle import goto
import utils
import threading
import time

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
    
    CODE = {
        "LIST": "LIST",
    }
    
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
        self.get_list_files_from_server(main_socket)
        
        # Create 4 more socket connections
        socket_list = self.open_socket_connections(main_socket)
        for socket in socket_list:
            print(f"[STATUS] Socket {socket} is open on {self.HOST}")

    def get_list_files_from_server(self, main_socket):
        message = "LIST\r\n"
        message = message.ljust(self.MESSAGE_SIZE)
        main_socket.sendto(message.encode(), (self.HOST, self.PORT))
        
        data, addr = main_socket.recvfrom(1024)
        data = data.decode()
        data = data.strip()
        message = data.split("\r\n")[0]
    
        if message == self.CODE['LIST']:
            list_file = data.split("\r\n")[1]
            # Convert data to list
            list_file = eval(list_file)

            print(utils.setTextColor("green"), end="")
            print(f"[RESPONE] List of available resources:")
            print(utils.setTextColor("white"), end="")
            for file in list_file:
                print(f"[LIST] |----------{file}----------|")
            print("Press Enter to continue...")
            input()
    
    def open_socket_connections(self, main_socket):
        message = "OPEN\r\n"
        message = message.ljust(self.MESSAGE_SIZE)
        main_socket.sendto(message.encode(), (self.HOST, self.PORT))
        print(utils.setTextColor("green"), end="")
        print(
            f"[STATUS] We will send data to {self.PIPES} streams of data at {self.HOST} by requesting on {main_socket} on the server"
        )
        print(utils.setTextColor("white"), end="")

        # Connect to master port to create 4 pipe
        socket_list = []
        for i in range(self.PIPES):
            data, addr = main_socket.recvfrom(1024)
            data = data.decode()
            data = data.strip()
            new_socket = int(data);
            print(f"[STATUS] We will receive data from server on port {new_socket}")
            
            socket_list.append(new_socket)
       
        # Print the status
        print(f"[STATUS] Connected to server {self.HOST} on 4 new ports")
        
        return socket_list 
            
s1 = SocketClientUDP()
s1.connect_to_server("input.txt")
         