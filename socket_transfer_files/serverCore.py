import socket
import threading

HOST='127.0.0.1'
PORT=6969

def handleSplitfile(filename):
    return

def handleClient(client_socket, port, reqFiles):
    print(f"Connected on {client_socket}")

    #Here is where server send data
    print(f"Transfering {reqFiles}...")
    client_socket.send(f"".encode())
    client_socket.close()


def createServer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Handle errors
        try:
            # Bind the socket to the address
            server_socket.bind((HOST, PORT))
        except OSError as e:
            print("Cannot create server!")
            return
        
        # Listen for incoming connections
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")
        # Wait for a connection
        conn, addr = server_socket.accept()
        print("Connected by", addr);

        # Receive a list of file you want to download
        reqFiles = conn.recv(1024).decode()
        print(f"Server want to get: {reqFiles}");

        # Open more 4 next ports for data transfer
        working_ports = [PORT + 1, PORT + 2, PORT + 3, PORT + 4]
        # Send these 4 ports to client
        conn.send(f"{working_ports}".encode())
        # Create 4 threads for data transfer        
        for port in working_ports:
            additional_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            additional_socket.bind((HOST, port))
            # Listen for only 1 incoming connections on additional ports
            additional_socket.listen(4)
            print(f"Listening on additional port {port}")
            
            # Accept connection on each additional port
            client_thread = threading.Thread(target=lambda: handleClient(additional_socket.accept()[0], port, reqFiles))
            client_thread.start()        

        # Close the connection
        conn.close()  
