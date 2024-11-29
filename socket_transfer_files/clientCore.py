from importlib import metadata
from re import T
import socket
import time
import json
import threading
import math
import os

HOST='127.0.0.1'
PORT=6969
INPUT_UPDATE_INTERVAL = 5
CHUNK_SIZE = 1024
HEADER_SIZE = 8
PIPES = 4
METADATA_SIZE = 1024
DELIMETER_SIZE = 2 # for \r\n

class SocketClient:
    def connect_to_server(self, filename):
        """
        Connect to the server and send the request to download the file.
        """
       
        # Read the input file
        with open(filename, 'r') as file:
            rows = file.readlines()
           
        # Connect to the main server port
        server_address = (HOST, PORT)
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            main_socket.connect(server_address)
        except ConnectionRefusedError:
            print(f"Server {HOST} is not running!")
            return
        
        # Receive the additional port numbers
        additional_ports = main_socket.recv(1024).decode()
        additional_ports = eval(additional_ports)  # Convert to list
        print(f"We will connect to 4 streams of data at {HOST} on port: {additional_ports}")

        # Connect to each additional port
        socket_list = []
        for port in additional_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, port))
            socket_list.append(sock)
            print(f"Connected to server {HOST} on port {port}")
         
        needed_files = self.read_input_file(filename)
        received_files = []
        cur_index = 0
        while len(received_files) < len(needed_files):
            # Reupdate list of files needed to download
            needed_files = self.read_input_file(filename)
            if (len(received_files) == len(needed_files)):
                break
            
            # Send request to server
            main_socket.send(needed_files[cur_index].encode())

            # get specific file from server
            metadata = self.receive_metadata(main_socket)
            metadata = eval(metadata)  # Convert to list
            print(metadata)
            
            # DEBUG
            res = self.receive_file_in_chunks(socket_list, "downloaded_" + needed_files[cur_index], metadata)
            if res:
                received_files.append(res)
                cur_index = cur_index + 1
           
               
            time.sleep(1)

        main_socket.close()

    def receive_metadata(self, conn):
        """
        Receive metadata from the server.
        """
        metadata = conn.recv(1024).decode()
        return metadata

    def read_input_file(self, filename):
        """
        Read the input file and return its content as a JSON string.
        """
        with open(filename, 'r') as file:
            rows = [line.strip() for line in file.readlines()]
            
        return rows

    def handle_pipe(self, pipe_socket):
        # DEBUG Here is where client receive data
        msg = pipe_socket.recv(1024).decode()
        print(msg, end="")
        pipe_socket.close()
        
    def receive_file_in_chunks(self, sockets, output_file, metadata):
        """
        Receive file chunks from multiple sockets and reassemble them.

        :param sockets: List of connected socket objects.
        :param output_file: Path to save the reassembled file.
        :param total_chunks: Total number of chunks to expect.
        """
        received_chunks = {}
        while len(received_chunks) < metadata[2]:
            try:
                data = sockets[0].recv(metadata[1])  # Allow space for sequence number
                if data:
                    # Extract sequence number and chunk
                    sequence_number, chunk = data.split(b"\r\n", 1)

                    received_chunks[int(sequence_number)] = chunk
                    print(f"{int(sequence_number)} : {metadata}")
                    print(f"Downloading file {output_file}: {math.trunc(int(sequence_number) / metadata[2] * 100)}%")
                    
                    # DEBUG
                    time.sleep(0.01)
            except BlockingIOError:
                continue  # Non-blocking socket, no data yet
        
        # Reassemble the file
        with open(output_file, 'wb') as file:
            for i in range(metadata[2]):
                file.write(received_chunks[i])
                
        # Check file size
        if self.get_file_size(output_file) == metadata[0]:
            print("Transfer file done")
            return output_file
        else:
            print("Transfer file failed")
            return None
   
    def get_file_size(self, filename):
        """
        Get the size of the file in bytes.
        """
        return os.path.getsize(filename)

