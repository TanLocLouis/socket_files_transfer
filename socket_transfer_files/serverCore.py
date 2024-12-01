from doctest import master
import socket
import os
import threading
import utils

class SocketServer:
    HOST=socket.gethostbyname(socket.gethostname())
    PORT=6969
    INPUT_UPDATE_INTERVAL = 1 # Musk be smaller then in client
    CHUNK_SIZE = 1048576 # 1 MB
    HEADER_SIZE = 8
    PIPES = 4
    DELIMETER_SIZE = 2 # for \r\n
    RESOURCE_PATH = './resources/'
    MESSAGE_SIZE = 256

    def __init__(self) -> None:
        print("[STATUS] Initializing the server...")        

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
                    conn, addr = server_socket.accept()
                    print(f"[STATUS] Server listening on {self.HOST}:{self.PORT}")
                    # Auto disconnect after 5 seconds
                    conn.settimeout(5)
                    print("[STATUS] Connected by", addr);
                   
                    client_thread = threading.Thread(target=self.handle_client_connection, args=(conn, addr))
                    client_thread.start()
            except KeyboardInterrupt:
                print("[STATUS] Server is shutting down...")
                server_socket.close()
                return

    def handle_client_connection(self, conn, addr):
        # Send a list of available resources to client
        self.send_resources_list(conn)
        
        # Open more 4 next pipes for data transfer by master port
        tmp = self.create_pipes(conn)
            
        # Server return specific chunk to client
        self.send_chunk(conn, tmp)
        
        # And also close the main server socket
        conn.close()

    def send_resources_list(self, conn):
        list_file = self.list_all_file_in_directory(self.RESOURCE_PATH)
        # Fill list file with space to make it match standard size
        list_file = self.standardize_str(str(list_file), self.MESSAGE_SIZE)
        conn.sendall(f"{list_file}".encode())
        
    def create_pipes(self, conn):
        master_port = self.find_free_port()
            
        # Send master to open 4 ports to client
        conn.sendall(f"{master_port}".encode())
        
        # Create 4 threads for data transfer    
        pipe_list = []
        master_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        master_socket.bind((self.HOST, master_port))
        tmp = []
        for _ in range(self.PIPES):
            # Listen for only 4 incoming connections on master ports
            master_socket.listen(1)
                      
            # Accept connection on each master port
            pipe_conn, addr = master_socket.accept()
            # Auto disconnect after 5 seconds
            pipe_conn.settimeout(5)
            print(f"[STATUS] Listening on master port {addr}")
            # pipe_list.append(threading.Thread(target=self.handlePipe, args=()).start())
            
            tmp.append(pipe_conn)
        return tmp
    
    def send_chunk(self, conn, tmp):
        try:
            while True:
                # Wait for the client to send the request for specific chunk
                chunk_offset = conn.recv(self.MESSAGE_SIZE).decode()
                if not chunk_offset:
                    print("[STATUS] Client disconnected")
                    break
                
                # Remove all ending space in chunk_offset
                print(f"[STATUS] Received request for chunk {chunk_offset.strip()}")

                filename, start_offset, end_offset = eval(chunk_offset.strip())
                with open(self.RESOURCE_PATH + filename, 'rb') as file:
                        file.seek(start_offset)
                        chunk = file.read(end_offset - start_offset + 1)
                        data = f"{chunk_offset}\r\n".encode() + chunk
                        tmp[(start_offset // self.CHUNK_SIZE) % 4].sendall(data)
                        print(f"[STATUS] Sent chunk {chunk_offset.strip()}")
        except ConnectionResetError:
            print("[ERROR] Connection forcibly closed by the client.")
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            # Ensure connections are properly closed
            conn.close()
            for pipe in tmp:
                pipe.close()
        
    def find_free_port(self):
        """
        Find a free port on the server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.HOST, 0))
            return s.getsockname()[1]
   
    def list_all_file_in_directory(self, dir):
        """
        List all files in the current directory.
        """
        files = os.listdir(dir)
        return files

    def standardize_str(self, s, n):
       while len(s) < n:
           s += ' '
       return s
