import socket
import time

HOST='127.0.0.1'
PORT=6969

class SocketClient:
    def readInputFile(self, filename):
        with open(filename, 'r') as file:
            rows = [line.strip() for line in file.readlines()]
        return rows

    def downloadFromServer(self, filename):
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
        
        # Send content you want to download on input.txt to server
        data = self.readInputFile(filename)
        main_socket.sendall(str(data).encode())

        # Receive the additional port numbers
        additional_ports = main_socket.recv(1024).decode()
        additional_ports = eval(additional_ports)  # Convert to list
        print(f"We will connect to 4 streams of data at {HOST} on port: {additional_ports}")

        # Connect to each additional port
        for port in additional_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, port))
            print(f"Connected to server {HOST} on port {port}")
            
            # DEBUG Here is where client receive data
            msg = sock.recv(1024).decode()
            print(msg)
            sock.close()
            time.sleep(5)
            
        main_socket.close()

