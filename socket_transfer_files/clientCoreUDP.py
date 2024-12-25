import socket
import utils
import math
import os
import threading
import time


class SocketClientUDP:
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 6969
    INPUT_UPDATE_INTERVAL = 5
    PIPES = 20

    CHUNK_SIZE = 32768  # 32 KB
    HEADER_SIZE = 8
    DELIMETER_SIZE = 2  # for \r\n
    MESSAGE_SIZE = 256
    
    CHECHSUM_LEN = 32
    TIMEOUT = 0.5 # 3 second for NAK 

    DOWNLOAD_DIR = os.getcwd()
    
    CODE = {
        "LIST": "LIST",
    }
    
    def connect_to_server(self, filename, download_dir, server_ip):
        """
        Connect to the server and send the request to download the file.
        """
        
        self.DOWNLOAD_DIR = download_dir
        self.HOST = server_ip
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.handle_server_connection(main_socket, filename)
        except Exception as e:
            print(utils.setTextColor("red"), end="")
            print(f"[ERROR] An error occurred: {e}")
            print(utils.setTextColor("white"), end="")
        finally:
            # Close the socket
            main_socket.close()
           
    def handle_server_connection(self, main_socket, filename):
        # Request list of available resources
        self.get_list_files_from_server(main_socket)
        
        # Create 4 more socket connections
        socket_list = self.open_socket_connections(main_socket)

        # Send the request to download the file
        self.send_request(socket_list, filename)
        
    def send_request(self, socket_list, filename):
        # Read the input file
        needed_files = self.parse_input_file(filename)
        received_files = []
        cur_index = 0
       
        while len(received_files) < len(needed_files):
            # Reupdate list of files needed to download
            needed_files = self.parse_input_file(filename)
            if len(received_files) >= len(needed_files):
                break

            # Check if the file is already downloaded
            if utils.check_file_exist(self.DOWNLOAD_DIR + needed_files[cur_index]["name"]):
                print(utils.setTextColor("green"), end="")
                print(
                    f"[STATUS] File {needed_files[cur_index]} has already been downloaded"
                )
                print(utils.setTextColor("white"), end="")
                received_files.append(needed_files[cur_index]["name"])
                cur_index += 1
                time.sleep(3)
                continue

            # Receive the chunk from the server
            self.receive_chunk(needed_files, cur_index, socket_list) 

            # Check file size to ensure file is transferred successfully
            cur_index += self.check_file_integrity(
                cur_index, needed_files, received_files
            )

            time.sleep(3)

        # Confirmation
        self.confirm_download(needed_files, received_files)

    def receive_chunk(self, needed_files, cur_index, socket_list):
        """
        Receive a chunk from the server.
        """
        # Send the chunk message which client want to download from server
        cur_file_size = needed_files[cur_index]["size_bytes"]
        filename = needed_files[cur_index]["name"]
 
        number_of_chunk = math.ceil(cur_file_size / self.CHUNK_SIZE)
        threads_list = [] 
        
        recv_chunk = dict()
        for chunk in range(number_of_chunk):
            # Print the status     
            print(
                f"[PROGRESS] Downloading file {filename}: {int(len(recv_chunk) / number_of_chunk * 100)}%..."
            )
        
            start_offset = chunk * self.CHUNK_SIZE
            end_offset = (chunk + 1) * self.CHUNK_SIZE - 1
            if end_offset > cur_file_size - 1:
                end_offset = cur_file_size - 1

            # Send message to server
            message = f"GET\r\n{filename}\r\n{needed_files[cur_index]['size_bytes']}\r\n{start_offset}\r\n{end_offset}\r\n"
            # print(f"[REQUEST] Requesting chunk {message}")
            # Make the message len MESSAGE_SIZE
            message = message.ljust(self.MESSAGE_SIZE)
            
            # Receive the chunk from server through 4 sockets
            id = start_offset // self.CHUNK_SIZE % self.PIPES
            
            time.sleep(0.01)                

            t = threading.Thread(
                target=self.handle_receive_chunk, args=(id, socket_list, message, chunk, filename, recv_chunk)
            )
            t.start()
            threads_list.append(t)
            
        for t in threads_list:
            t.join()    

        print("[STATUS] All chunks has been received: 100%")
        
        # Concatenate those files
        for chunk in range(number_of_chunk):
            with open(f"{self.DOWNLOAD_DIR}{needed_files[cur_index]['name']}", "ab") as file:
                file.write(recv_chunk[chunk])

    recv_seq = set()
    def handle_receive_chunk(self, id, socket_list, message, chunk, filename, recv_chunk):
        slave = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        slave.settimeout(self.TIMEOUT)       
        
        # rdt checksum, timeout, dict()
        is_checksum_matched = False
        isNAK = False;
        while not is_checksum_matched:
            # Send the message to server    
            slave.sendto(message.encode(), (self.HOST, socket_list[id]))
            try:
                data, addr = slave.recvfrom(self.CHECHSUM_LEN + self.DELIMETER_SIZE + self.MESSAGE_SIZE + self.DELIMETER_SIZE + self.CHUNK_SIZE)
            except:
                isNAK = True
            if isNAK:
                isNAK = False
                # Reopen socket
                slave = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                continue 

            # print(f"[RESPOND] Received chunk successful")
            if data:
                checksum = data[:self.CHECHSUM_LEN]
                
                chunk_data = data[self.CHECHSUM_LEN + self.DELIMETER_SIZE + self.MESSAGE_SIZE + self.DELIMETER_SIZE:]
                chunk_data_checksum = utils.calculate_checksum(chunk_data)
                if chunk_data_checksum != checksum:
                    print(utils.setTextColor("red"), end="")
                    print(f"[ERROR] Checksum is not matched")
                    print(utils.setTextColor("white"), end="")
                    continue
                else:
                    is_checksum_matched = True
               
                # Check if the chunk is duplicate
                if checksum in self.recv_seq:
                    print(utils.setTextColor("red"), end="")
                    print(f"[ERROR] Duplicate chunk skipped")
                    print(utils.setTextColor("white"), end="")
                    continue
                else:
                    self.recv_seq.add(checksum)
                
                recv_chunk[chunk] = chunk_data
        
    def get_list_files_from_server(self, main_socket):
        message = "LIST\r\n"
        message = message.ljust(self.MESSAGE_SIZE)
        main_socket.sendto(message.encode(), (self.HOST, self.PORT))
        
        data, addr = main_socket.recvfrom(self.MESSAGE_SIZE)
        data = data.decode()
        data = data.strip()
        message = data.split("\r\n")[0]
    
        if message == self.CODE['LIST']:
            list_file = data.split("\r\n")[1]
            # Convert data to list
            list_file = eval(list_file)

            print(utils.setTextColor("green"), end="")
            print(f"[RESPOND] List of available resources:")
            print(utils.setTextColor("white"), end="")
            print(50*"-")
            for file in list_file:
                print(file)
            print(50*"-")
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
            data, addr = main_socket.recvfrom(self.MESSAGE_SIZE)
            data = data.decode()
            data = data.strip()
            new_socket = int(data);
            print(f"[STATUS] We will receive data from server on port {new_socket}")
            
            socket_list.append(new_socket)
       
        # Print the status
        print(f"[STATUS] Connected to server {self.HOST} on 4 new ports")
        
        return socket_list 
    
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
            with open(file_path, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        # Split the line into components
                        parts = line.split()
                        if len(parts) == 2:
                            name, size = parts
                            # Parse size in bytes
                            size_bytes = int(size[:-1].replace(",", ""))
                            # Append the data as a dictionary
                            data.append(
                                {"name": name, "size": size, "size_bytes": size_bytes}
                            )
        except Exception as e:
            print(utils.setTextColor("red"), end="")
            print(f"[ERROR] An error occurred: {e}")
            print(utils.setTextColor("white"), end="")

        return data
    
    def check_file_integrity(self, cur_index, needed_files, received_files):
        if (
            utils.get_file_size(self.DOWNLOAD_DIR + needed_files[cur_index]["name"])
            == needed_files[cur_index]["size_bytes"]
        ):
            print(utils.setTextColor("green"), end="")
            print(
                 f"[SUCCESS] File {needed_files[cur_index]} has been downloaded successfully"
            )
            print(utils.setTextColor("white"), end="")
            received_files.append(needed_files[cur_index]["name"])
            return 1
        else:
            print(utils.setTextColor("green"), end="")
            print(
            f"[FAIL] File {needed_files[cur_index]} has been downloaded unsuccessfully"
            )
            print(
            f"[DETAIL] Expected file size: {needed_files[cur_index]['size_bytes']} bytes"
            )
            print(
            f"[DETAIL] Received file size: {utils.get_file_size(needed_files[cur_index]['name'])} bytes"
            )
            print(utils.setTextColor("white"), end="")
            return 0

    def confirm_download(self, needed_files, received_files):
        print(utils.setTextColor("green"), end="")
        print(f"Downloads successfully {len(received_files)}/{len(needed_files)} files")
        print(utils.setTextColor("white"), end="") 