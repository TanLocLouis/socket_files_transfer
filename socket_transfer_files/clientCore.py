import socket

HOST='127.0.0.1'
PORT=6969

def downloadFromServer(filename):
    with open(filename, 'r') as file:
        rows = file.readlines()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((HOST, PORT))
        except ConnectionRefusedError as e:
            print(f"Error: {e}")
            return
        
        client_socket.sendall(b"Hello, server")
        data = client_socket.recv(1024)

        print("Received from server:", data.decode())
