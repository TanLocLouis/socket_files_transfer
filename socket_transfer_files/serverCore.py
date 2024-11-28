from msvcrt import kbhit
from site import makepath
import socket
import threading
import time
import json
import os

HOST='127.0.0.1'
PORT=6969
INPUT_UPDATE_INTERVAL = 1 # Musk be smaller then in client
CHUNK_SIZE = 1024
HEADER_SIZE = 8
PIPES = 4
METADATA_SIZE = 1024
DELIMETER_SIZE = 2 # for \r\n

class SocketServer:
    def __init__(self) -> None:
        print("Initializing the server...")        

    def create_server(self):
        """
        Create a server that listens for incoming connections.
        """
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Handle errors
            try:
                # Bind the socket to the address
                server_socket.bind((HOST, PORT))
            except OSError as e:
                print("Cannot create server!")
                return
            
            # Listen for incoming connections
            server_socket.listen()
            print(f"Server listening on {HOST}:{PORT}")
            # Wait for a connection
            conn, addr = server_socket.accept()
            print("Connected by", addr);
           
            # Open more 4 next ports for data transfer
            working_ports = [PORT + 1, PORT + 2, PORT + 3, PORT + 4]
            # Send these 4 ports to client
            conn.send(f"{working_ports}".encode())
            
            # Create 4 threads for data transfer    
            pipe_list = []
            for port in working_ports:
                additional_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                additional_socket.bind((HOST, port))
                # Listen for only 1 incoming connections on additional ports
                additional_socket.listen(4)
                print(f"Listening on additional port {port}")
                          
                # Accept connection on each additional port
                pipe_conn, addr = additional_socket.accept()
                pipe_list.append(pipe_conn)            
           

            # Send metadata
            self.send_meta_data("elon.png", conn)
            self.sendfile_in_chunks("elon.png", pipe_list)
            
            # And also close the main server socket
            conn.close()
           
    def send_meta_data(self, filename, conn):
        """
        Send metadata to the client.
        """
        file_size = self.get_file_size("elon.png");
        
        # Send metadata to client
        chunk_number = file_size // CHUNK_SIZE 
        metadata = [file_size, CHUNK_SIZE + HEADER_SIZE + DELIMETER_SIZE, chunk_number]
        conn.send(f"{metadata}".encode())             

    def get_file_size(self, filename):
        """
        Get the size of the file in bytes.
        """
        return os.path.getsize(filename)

    def sendfile_in_chunks(self, file_path, sockets):
        """
        Send a file in chunks over multiple sockets.

        :param file_path: Path to the file to send.
        :param sockets: List of socket connections.
        """
        chunk_size = CHUNK_SIZE  # Size of each chunk
        with open(file_path, 'rb') as file:
            chunk_number = 0 
                
            while chunk := file.read(chunk_size):
                chunk_number_str = str(chunk_number)
                chunk_number_str = self.standardize_str(chunk_number_str, HEADER_SIZE)
                    
                # Prepare data with sequence number
                data = f"{chunk_number_str}\r\n".encode() + chunk
                # Send data over one of the sockets (e.g., round-robin)
                sockets[0].sendall(data)
                chunk_number += 1
                
    def standardize_str(self, s, n):
       while len(s) < n:
           s = '0' + s
       return s
