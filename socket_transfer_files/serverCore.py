import socket
import threading

HOST='127.0.0.1'
PORT=6969

def handleClient(client_socket, port):
    print(f"Connected on port {port}")
    client_socket.send(f"Connected to port {port}".encode())
    client_socket.close()

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
        
        # Open more 4 ports for data transfer
        working_ports = [6970, 6971, 6972, 6973]
        # Send these 4 ports to client
        conn.send(f"{working_ports}".encode())
        # Create 4 threads for data transfer        
        for port in working_ports:
            additional_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            additional_socket.bind((HOST, port))
            # Listen for only 1 incoming connections on additional ports
            additional_socket.listen(1)
            print(f"Listening on additional port {port}")
            
            # Accept connection on each additional port
            client_thread = threading.Thread(target=lambda: handleClient(additional_socket.accept()[0], port))
            client_thread.start()

        # Close the connection
        conn.close()  
