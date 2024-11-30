import socket
import os
import threading

HOST='127.0.0.1'
PORT=6969
INPUT_UPDATE_INTERVAL = 1 # Musk be smaller then in client
CHUNK_SIZE = 1024
HEADER_SIZE = 8
PIPES = 4
METADATA_SIZE = 1024
DELIMETER_SIZE = 2 # for \r\n
RESOURCE_PATH = './resources/'

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
            except Exception as e:
                print(e)
                return
            
            # Listen for incoming connections
            server_socket.listen()
            print(f"Server listening on {HOST}:{PORT}")
            # Wait for a connection
            conn, addr = server_socket.accept()
            print("Connected by", addr);
           
            client_thread = threading.Thread(target=self.handle_client_connection, args=(conn, addr))
            client_thread.start()
            
    def handle_client_connection(self, conn, addr):
        # Send a list of available resources to client
        list_file = self.list_all_file_in_directory(RESOURCE_PATH)
        conn.sendall(f"{list_file}".encode())

        # Open more 4 next ports for data transfer
        working_ports = []
        for i in range(4):
            port = self.find_free_port()
            working_ports.append(port)
            
        # Send these 4 ports to client
        conn.sendall(f"{working_ports}".encode())
        
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
       
        while True:
            # Wait for the client to send the request
            filename = conn.recv(1024).decode()
            
            # Send metadata
            self.send_meta_data(RESOURCE_PATH + filename, conn)
            self.sendfile_in_chunks(RESOURCE_PATH + filename, pipe_list)
        
        # And also close the main server socket
        conn.close()
           
    def send_meta_data(self, filename, conn):
        """
        Send metadata to the client.
        """
        file_size = self.get_file_size(filename);
        
        # Send metadata to client
        chunk_number = file_size // CHUNK_SIZE 
        metadata = [file_size, CHUNK_SIZE + HEADER_SIZE + DELIMETER_SIZE, chunk_number + 1, CHUNK_SIZE]
        conn.sendall(f"{metadata}".encode())             

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
                
                sockets[chunk_number % PIPES].sendall(data)
                chunk_number += 1
        
    def find_free_port(self):
        """
        Find a free port on the server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, 0))
            return s.getsockname()[1]
   
    def list_all_file_in_directory(self, dir):
        """
        List all files in the current directory.
        """
        files = os.listdir(dir)
        return files

    def standardize_str(self, s, n):
       while len(s) < n:
           s = '0' + s
       return s
