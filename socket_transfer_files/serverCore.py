import socket
import os
import threading
import time

HOST=socket.gethostbyname(socket.gethostname())
PORT=6969
INPUT_UPDATE_INTERVAL = 1 # Musk be smaller then in client
CHUNK_SIZE = 1024
HEADER_SIZE = 8
PIPES = 4
DELIMETER_SIZE = 2 # for \r\n
RESOURCE_PATH = './resources/'
MESSAGE_SIZE = 256

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

        # Open more 4 next ports for data transfer by master port
        master_port = self.find_free_port()
            
        # Send master to open 4 ports to client
        conn.sendall(f"{master_port}".encode())
        
        # Create 4 threads for data transfer    
        pipe_list = []
        master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master_socket.bind((HOST, master_port))
        for i in range(PIPES):
            # Listen for only 4 incoming connections on master ports
            master_socket.listen(1)
                      
            # Accept connection on each master port
            pipe_conn, addr = master_socket.accept()
            print(f"Listening on master port {addr}")
            pipe_list.append(pipe_conn)
       
        while True:
            # Wait for the client to send the request for specific chunk
            chunk_offset = conn.recv(MESSAGE_SIZE).decode()
            # Remove all ending space in chunk_offset
            print(f"Received request for chunk {chunk_offset.strip()}")

            # Server return specific chunk to client
            self.send_chunk(chunk_offset, conn)
        
        # And also close the main server socket
        conn.close()
    
    def send_chunk(self, chunk_offset, conn):
        filename, start_offset, end_offset = eval(chunk_offset.strip())
        with open(RESOURCE_PATH + filename, 'rb') as file:
                file.seek(start_offset)
                chunk = file.read(end_offset - start_offset + 1)
                data = f"{chunk_offset}\r\n".encode() + chunk
                conn.sendall(data)
                print(f"Sent chunk {chunk_offset.strip()}")
        
    def get_file_size(self, filename):
        """
        Get the size of the file in bytes.
        """
        return os.path.getsize(filename)
        
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
