import socket
import threading
import utils


class SocketServerUDP:
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 6969
    HEADER_SIZE = 8
    PIPES = 10
    RESOURCE_PATH = "./resources/"
    MESSAGE_SIZE = 256
    TIMEOUT = 600

    CODE = {
        "LIST": "LIST",
        "OPEN": "OPEN",
        "GET": "GET",
        "ACK": "ACK"
    }

    def __init__(self) -> None:
        print("[STATUS] Initializing the UDP server...")

    def create_server(self):
        """
        Create a server that listens for incoming connections.
        """

        # HOST = 
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            # Handle errors
            try:
                print(f"Server is listening on {self.HOST}:{self.PORT}")
                # Bind the socket to the address
                server_socket.bind((self.HOST, self.PORT))
                self.handle_client_connection(server_socket)    
            except Exception as e:
                print(f"[ERROR] {e}")
                return

    def handle_client_connection(self, server_socket):
        try:
            while True:
                # Wait for a connection
                data, addr = server_socket.recvfrom(1024)
                data = data.decode()
                data = data.strip()
                # Split \r\n from message
                message = data.split("\r\n")[0]
               
                # Send a list of available resources to client
                if message == self.CODE['LIST']:
                    print("[REQUEST] Client request list of available resources...")
                    self.send_resources_list(server_socket, addr)
                    
                # Open more 4 socket connections
                if message == self.CODE['OPEN']:
                    # Create a new thread to handle the new connection
                    print(f"[REQUEST] Client request to open more {self.PIPES} sockets...")
                    self.create_pipes(server_socket, addr)

                # Send a chunk
                if message == self.CODE['GET']:
                    print("[REQUEST] Client request chunk...")
                # ACK from client
                if message == self.CODE['ACK']:
                    print("[REQUEST] Client ACK for...")

        except KeyboardInterrupt:
            print("[STATUS] Server is shutting down...")
            server_socket.close()
            return
       
    def send_resources_list(self, server_socket, addr):
        """
        Send a list of available resources to client.
        """
        # Get all files in the resources folder
        files = utils.list_all_file_in_directory(self.RESOURCE_PATH)
        # Convert to string
        files = "LIST\r\n" + str(files)
        files.ljust(self.MESSAGE_SIZE)
        # Send the list of available resources to client
        server_socket.sendto(files.encode(), addr)
       
    def create_pipes(self, server_socket, addr):
        """
        Open more socket connections.
        """
        pipes_list = []
        for i in range(self.PIPES):
            # Find free port
            free_port = utils.find_free_port_UDP(self.HOST);
            print(f"[STATUS] Found free port: {free_port} for client {addr[0]}:{addr[1]}")
            # Send the port to client
            server_socket.sendto(f"{free_port}".ljust(self.MESSAGE_SIZE).encode(), addr)
            
            # Create a new socket connection
            t = threading.Thread(target=self.handle_create_pipes, args=(free_port, ))
            t.start()
            pipes_list.append(free_port)
            
        return pipes_list
            
    def handle_create_pipes(self, free_port):
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        new_socket.bind((self.HOST, free_port))
        new_socket.settimeout(self.TIMEOUT)
        
        while True:
            data, addr = new_socket.recvfrom(self.MESSAGE_SIZE)
            data = data.decode()
            message = data.split("\r\n")[0]
            filename = data.split("\r\n")[1]
            filesize = data.split("\r\n")[2]
            start_offset = int(data.split("\r\n")[3])
            end_offset = int(data.split("\r\n")[4])
            
            if message == self.CODE['GET']: 
                print(f"[REQUEST] Client {addr} request chunk {data.strip()} to {addr}") 
                with open(self.RESOURCE_PATH + filename, "rb") as file:
                    file.seek(start_offset)
                    chunk = file.read(end_offset - start_offset + 1)
                    checksum = utils.calculate_checksum(chunk)
                    send_data = checksum + f"\r\n{data}\r\n".encode() + chunk
                    
                    new_socket.sendto(send_data, addr);
                    print(f"[RESPOND] Sent chunk {data.strip()} to {addr}")
        
