import socket
import os
import threading

class SocketServerUDP:
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 6969
    HEADER_SIZE = 8
    PIPES = 4
    RESOURCE_PATH = "./resources/"
    MESSAGE_SIZE = 256

    def __init__(self) -> None:
        print("[STATUS] Initializing the server...")

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
                print(f"[REQUEST] Request from {addr}: {data}")

        except KeyboardInterrupt:
            print("[STATUS] Server is shutting down...")
            server_socket.close()
            return
        
s1 = SocketServerUDP()
s1.create_server()
            