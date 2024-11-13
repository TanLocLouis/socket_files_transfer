import socket
import threading

HOST='127.0.0.1'
PORT=6969

def createServer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Bind the socket to the address
        try:
            server_socket.bind((HOST, PORT))
            
        # Handle errors
        except OSError as e:
            print(f"Error: {e}")
            return
        
        # Listen for incoming connections
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")
       
        # Wait for a connection
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print("Received from client:", data.decode())
                conn.sendall(b"Message received")
