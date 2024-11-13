import socket

HOST='127.0.0.1'
PORT=6969

def downloadFromServer(filename):
    with open(filename, 'r') as file:
        rows = file.readlines()
       
    # Connect to the main server port
    server_address = (HOST, PORT)
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.connect(server_address)

    # Receive the additional port numbers
    additional_ports = main_socket.recv(1024).decode()
    additional_ports = eval(additional_ports)  # Convert to list
    print(f"Received additional ports: {additional_ports}")

    # Connect to each additional port
    for port in additional_ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', port))
        print(f"Connected to server on port {port}")
        
        # Receive confirmation from server
        msg = sock.recv(1024).decode()
        print(f"Server says: {msg}")
        sock.close()
        
    main_socket.close()

