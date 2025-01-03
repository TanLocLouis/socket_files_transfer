import socket
import threading
import utils


class SocketServer:
    HOST = "192.168.31.181"
    PORT = 6969
    HEADER_SIZE = 8
    PIPES = 4
    RESOURCE_PATH = "./resources/"
    MESSAGE_SIZE = 1024
    TIMEOUT = 600 
    
    CODE = {
        "LIST": "LIST",
        "OPEN": "OPEN",
        "GET": "GET"
    }

    def __init__(self) -> None:
        print("[STATUS] Initializing the TCP server...")

    def create_server(self):
        """
        Create a server that listens for incoming connections.
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Handle errors
            try:
                # Bind the socket to the address
                server_socket.bind((self.HOST, self.PORT))
            except Exception as e:
                print(f"[ERROR] {e}")
                return

            try:
                while True:
                    # Listen for incoming connections
                    server_socket.listen()
                    # Wait for a connection
                    print(f"[STATUS] Server listening on {self.HOST}:{self.PORT}")
                    master, addr = server_socket.accept()
                    # Auto disconnect after 10 seconds
                    master.settimeout(self.TIMEOUT)
                    print("[STATUS] Connected by", addr)

                    client_thread = threading.Thread(
                        target=self.handle_client_connection, args=(master, addr)
                    )
                    client_thread.start()
            except KeyboardInterrupt:
                print("[STATUS] Server is shutting down...")
                server_socket.close()
                return

    def handle_client_connection(self, master, addr):
        pipes_list = []
        
        while True:
            data = master.recv(self.MESSAGE_SIZE)
            data = data.decode()
            data = data.strip()
            message = data.split("\r\n")[0]
            
            if message == self.CODE["LIST"]:    
                # Send a list of available resources to client
                self.send_resources_list(master)
            elif message == self.CODE["OPEN"]:
                # Open more 4 next pipes for data transfer by master port
                # Return a list of pipes
                pipes_list = self.create_pipes(master)
            elif message == self.CODE["GET"]:
                # Server return specific chunk to client
                payload = data.split("\r\n")[1]
                self.send_chunk(master, payload, addr, pipes_list)

    def send_resources_list(self, master):
        list_file = utils.list_all_file_in_directory(self.RESOURCE_PATH)
        # Fill list file with space to make it match standard size
        list_file = utils.standardize_str(str(list_file), self.MESSAGE_SIZE)
        master.sendall(f"{list_file}".encode())

    def create_pipes(self, master):
        master_port = utils.find_free_port(self.HOST)

        # Send master to open 4 ports to client
        master.sendall(f"{master_port}".encode())

        # Create 4 threads for data transfer
        master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master_socket.bind((self.HOST, master_port))
        pipes_list = []
        for _ in range(self.PIPES):
            # Listen for only 4 incoming connections on master ports
            master_socket.listen(1)

            # Accept connection on each master port
            pipe_conn, addr = master_socket.accept()
            # Auto disconnect after 10 seconds
            pipe_conn.settimeout(self.TIMEOUT)
            print(f"[STATUS] Listening on master port {addr}")
            # pipe_list.append(threading.Thread(target=self.handlePipe, args=()).start())

            pipes_list.append(pipe_conn)
        return pipes_list

    def send_chunk(self, master, message, addr, pipes_list):
        # Wait for the client to send the request for specific chunk
        if not message:
            print("[STATUS] Client disconnected")

        # Remove all ending space in chunk_offset
        print(f"[REQUEST] Received request for chunk {message.strip()} from {addr}")

        t = threading.Thread(target=self.handle_send_chunk, args=(message, pipes_list))
        t.start()
        t.join()            

    def handle_send_chunk(self, message, pipes_list):
        filename, file_size, start_offset, end_offset = eval(message.strip())
        with open(self.RESOURCE_PATH + filename, "rb") as file:
            file.seek(start_offset)
            chunk = file.read(end_offset - start_offset + 1)
            message = message.ljust(self.MESSAGE_SIZE)
            data = f"{message}\r\n".encode() + chunk

            self.CHUNK_SIZE = end_offset - start_offset + 1
            id = (start_offset // self.CHUNK_SIZE) % self.PIPES
            pipes_list[id].sendall(data)
            print(f"[RESPOND] Sent chunk {message.strip()} to {pipes_list[id]}")
