from doctest import master
import socket
import time
import math
import os
import utils

from serverCore import RESOURCE_PATH

HOST='192.168.56.1'
PORT=6969
INPUT_UPDATE_INTERVAL = 5
PIPES = 4
METADATA_SIZE = 1024

CHUNK_SIZE = 1024
HEADER_SIZE = 8
DELIMETER_SIZE = 2 # for \r\n
MESSAGE_SIZE = 256

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
        except Exception as e:
            print(e)
            return
        
        self.handle_server_connection(filename, main_socket)
        main_socket.close()
     
    def handle_server_connection(self, filename, main_socket):
        # Receive a list of available resources from server can be downloaded
        list_file = main_socket.recv(1024).decode()
        list_file = eval(list_file)  # Convert to list
        print(utils.setTextColor('green'), end="")
        print(f"List of available resources:")
        print(utils.setTextColor('white'), end="")
        for file in list_file:
            print(f"|----------{file}----------|")
        print("Press Enter to continue...")
        input()

        # Receive the additional port numbers
        master_port = main_socket.recv(1024).decode()
        print(utils.setTextColor('green'), end="")
        print(f"We will connect to 4 streams of data at {HOST} by requesting on port {master_port} on the server")
        print(utils.setTextColor('white'), end="")

        # Connect to master port to create 4 pipe
        socket_list = []
        for i in range(PIPES):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, int(master_port)))
            socket_list.append(sock)
        print(f"Connected to server {HOST} on 4 new ports")
        
        needed_files = self.parse_input_file(filename)
        received_files = []
        cur_index = 0
        while len(received_files) < len(needed_files):
            # Reupdate list of files needed to download
            needed_files = self.parse_input_file(filename)
            if (len(received_files) >= len(needed_files)):
                break
         
            # Receive the chunk from the server
            self.receive_chunk(needed_files, cur_index, main_socket)          
            
            # Check file size to ensure file is transferred successfully
            if self.get_file_size(RESOURCE_PATH + needed_files[cur_index]['name']) == needed_files[cur_index]['size_bytes']:
                print(utils.setTextColor('green'), end="")
                print(f"File {needed_files[cur_index]} has been downloaded successfully")
                print(utils.setTextColor('white'), end="")
                received_files.append(needed_files[cur_index]['name'])
                cur_index += 1
            else:
                print(utils.setTextColor('green'), end="")
                print(f"File {needed_files[cur_index]} has been downloaded unsuccessfully")
                print(utils.setTextColor('white'), end="")
            
            time.sleep(3)

        # Confirmation
        print(utils.setTextColor('green'), end="")
        print(f"Downloads successfully {len(received_files)}/{len(needed_files)} files")        
        print(utils.setTextColor('white'), end="")

    def receive_chunk(self, needed_files, cur_index, main_socket):
        """
        Receive a chunk from the server.
        """
       # Send the chunk message which client want to download from server
        cur_file_size = needed_files[cur_index]['size_bytes']
        number_of_chunk = cur_file_size // CHUNK_SIZE
        for chunk in range(number_of_chunk):
            start_offset = chunk * CHUNK_SIZE
            end_offset = (chunk + 1) * CHUNK_SIZE - 1
            if end_offset > cur_file_size - 1:
                end_offset = cur_file_size - 1
           
            # Send message to server
            message = [needed_files[cur_index]['name'], start_offset, end_offset]
            print(f"Requesting chunk {message}")
            # Make the message len 1024
            message = str(message).ljust(MESSAGE_SIZE)
            main_socket.sendall(message.encode())
            
            # Receive the chunk from server
            data = main_socket.recv(MESSAGE_SIZE + DELIMETER_SIZE + CHUNK_SIZE)
            if data:
                message, chunk_data = data.split(b"\r\n", 1)
                
                # Progress bar
                print(f"Downloading file {needed_files[cur_index]}: {math.trunc(chunk / number_of_chunk * 100)}%")
                
                # Emiminate the sequence number spaces
                # Get the sequence number of the chunk
                print(f"Received chunk {message.strip()}")
                
                with open(f"downloaded_{needed_files[cur_index]['name']}", 'ab') as file:
                    file.write(chunk_data)

  
    def get_file_size(self, filename):
        """
        Get the size of the file in bytes.
        """
        return os.path.getsize(filename)

    def parse_input_file(self, file_path):
        """
        Reads a file with image data and returns a list of dictionaries with the parsed data.
        
        Args:
            file_path (str): The path to the file containing the image data.
        
        Returns:
            list: A list of dictionaries with keys 'name', 'size', and 'size_bytes'.
        """
        data = []
        
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        # Split the line into components
                        parts = line.split()
                        if len(parts) == 2:
                            name, size = parts
                            # Parse size in bytes
                            size_bytes = int(size[:-1].replace(',', ''))
                            # Append the data as a dictionary
                            data.append({
                                'name': name,
                                'size': size,
                                'size_bytes': size_bytes
                            })
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return data
