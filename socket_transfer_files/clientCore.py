import socket
import time
import math
import utils
import threading
import os


class SocketClient:
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 6969
    INPUT_UPDATE_INTERVAL = 5
    PIPES = 4
    METADATA_SIZE = 1024

    CHUNK_SIZE = 1048576  # 1 MB
    HEADER_SIZE = 8
    DELIMETER_SIZE = 2  # for \r\n
    MESSAGE_SIZE = 256

    def connect_to_server(self, filename):
        """
        Connect to the server and send the request to download the file.
        """

        # Read the input file
        with open(filename, "r") as file:
            rows = file.readlines()

        # Connect to the main server port
        server_address = (self.HOST, self.PORT)
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            main_socket.connect(server_address)
        except Exception as e:
            print(utils.setTextColor("red"), end="")
            print(f"[ERROR] An error occurred: {e}")
            print(utils.setTextColor("white"), end="")
            return

        self.handle_server_connection(filename, main_socket)
        main_socket.close()

    def handle_server_connection(self, filename, main_socket):
        # Receive a list of available resources from server can be downloaded
        list_file = self.receive_resource_list(main_socket)

        # Remove the spaces
        list_file = list_file.strip()
        list_file = eval(list_file)  # Convert to list

        print(utils.setTextColor("green"), end="")
        print(f"[RESPONE] List of available resources:")
        print(utils.setTextColor("white"), end="")
        for file in list_file:
            print(f"[LIST] |----------{file}----------|")
        print("Press Enter to continue...")
        input()

        # Create 4 pipes for data transfer
        socket_list = self.create_pipes(main_socket)

        # Read the input file
        needed_files = self.parse_input_file(filename)
        received_files = []
        cur_index = 0
        while len(received_files) < len(needed_files):
            # Reupdate list of files needed to download
            needed_files = self.parse_input_file(filename)
            if len(received_files) >= len(needed_files):
                break

            # Check if the file is already downloaded
            if utils.check_file_exist(needed_files[cur_index]["name"]):
                print(utils.setTextColor("green"), end="")
                print(
                    f"[STATUS] File {needed_files[cur_index]} has already been downloaded"
                )
                print(utils.setTextColor("white"), end="")
                received_files.append(needed_files[cur_index]["name"])
                cur_index += 1
                time.sleep(3)
                continue

            # Receive the chunk from the server
            self.receive_chunk(needed_files, cur_index, main_socket, socket_list)

            # Check file size to ensure file is transferred successfully
            cur_index += self.check_file_integrity(
                cur_index, needed_files, received_files
            )

            time.sleep(3)

        # Confirmation
        self.confirm_download(needed_files, received_files)

    def receive_resource_list(self, main_socket):
        list_file = main_socket.recv(self.MESSAGE_SIZE).decode()
        return list_file

    def create_pipes(self, main_socket):
        # Receive the additional port numbers
        master_port = main_socket.recv(self.MESSAGE_SIZE).decode()
        print(utils.setTextColor("green"), end="")
        print(
            f"[STATUS] We will connect to 4 streams of data at {self.HOST} by requesting on port {master_port} on the server"
        )
        print(utils.setTextColor("white"), end="")

        # Connect to master port to create 4 pipe
        socket_list = []
        for i in range(self.PIPES):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.HOST, int(master_port)))
            socket_list.append(sock)
        print(f"[STATUS] Connected to server {self.HOST} on 4 new ports")
        return socket_list

    def receive_chunk(self, needed_files, cur_index, main_socket, socket_list):
        """
        Receive a chunk from the server.
        """
        # Send the chunk message which client want to download from server
        cur_file_size = needed_files[cur_index]["size_bytes"]

        self.CHUNK_SIZE = math.ceil(cur_file_size / self.PIPES)
        number_of_chunk = math.ceil(cur_file_size / self.CHUNK_SIZE)
        threads_list = []

        for chunk in range(number_of_chunk):
            start_offset = chunk * self.CHUNK_SIZE
            end_offset = (chunk + 1) * self.CHUNK_SIZE - 1
            if end_offset > cur_file_size - 1:
                end_offset = cur_file_size - 1

            # Send message to server
            message = [
                needed_files[cur_index]["name"],
                cur_file_size,
                start_offset,
                end_offset,
            ]
            print(f"[REQUEST] Requesting chunk {message}")
            # Make the message len MESSAGE_SIZE
            message = str(message).ljust(self.MESSAGE_SIZE)
            main_socket.sendall(message.encode())

            # Receive the chunk from server through 4 pipes
            id = start_offset // self.CHUNK_SIZE % self.PIPES
            t = threading.Thread(
                target=self.handle_receive_chunk, args=(id, socket_list)
            )
            t.start()
            threads_list.append(t)

        for t in threads_list:
            t.join()
        print("[STATUS] All chunks has been received: 100%")

        # Concat those files
        for id in range(self.PIPES):
            with open(f"{needed_files[cur_index]['name']}", "ab") as file:
                with open(
                    f"{needed_files[cur_index]['name']}_{id}", "rb"
                ) as chunk_file:
                    file.write(chunk_file.read())
                os.remove(f"{needed_files[cur_index]['name']}_{id}")

    def handle_receive_chunk(
        self,
        id,
        socket_list,
    ):
        data = socket_list[id].recv(
            self.MESSAGE_SIZE + self.DELIMETER_SIZE + self.CHUNK_SIZE
        )
        if data:
            message, chunk_data = data.split(b"\r\n", 1)
            filename, file_size, start_offset, end_offset = eval(message.strip())

            # Progress bar
            print(
                f"[STATUS] Downloading file {filename}: {int(utils.count_files_with_prefix("./", filename) / self.PIPES * 100)}%"
            )

            print(f"[RESPOND] Received chunk {message.strip()}")

            with open(f"{filename}_{id}", "wb") as file:
                file.write(chunk_data)

    def check_file_integrity(self, cur_index, needed_files, received_files):
        if (
            utils.get_file_size(needed_files[cur_index]["name"])
            == needed_files[cur_index]["size_bytes"]
        ):
            print(utils.setTextColor("green"), end="")
            print(
                f"[SUCCESS] File {needed_files[cur_index]} has been downloaded successfully"
            )
            print(utils.setTextColor("white"), end="")
            received_files.append(needed_files[cur_index]["name"])
            return 1
        else:
            print(utils.setTextColor("green"), end="")
            print(
                f"[FAIL] File {needed_files[cur_index]} has been downloaded unsuccessfully"
            )
            print(
                f"[DETAIL] Expected file size: {needed_files[cur_index]['size_bytes']} bytes"
            )
            print(
                f"[DETAIL] Received file size: {utils.get_file_size(needed_files[cur_index]['name'])} bytes"
            )
            print(utils.setTextColor("white"), end="")
            return 0

    def confirm_download(self, needed_files, received_files):
        print(utils.setTextColor("green"), end="")
        print(f"Downloads successfully {len(received_files)}/{len(needed_files)} files")
        print(utils.setTextColor("white"), end="")

    def parse_input_file(self, file_path):
        """
        Reads a file with image data and returns a list of dictionaries with the parsed data.

        Args:
            file_path (str): The path to the file containing the image data.

        Returns:
            list: A list of dictionaries with keys 'name', 'size', and 'size_bytes'.
        """
        data = []

        try:
            with open(file_path, "r") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        # Split the line into components
                        parts = line.split()
                        if len(parts) == 2:
                            name, size = parts
                            # Parse size in bytes
                            size_bytes = int(size[:-1].replace(",", ""))
                            # Append the data as a dictionary
                            data.append(
                                {"name": name, "size": size, "size_bytes": size_bytes}
                            )
        except Exception as e:
            print(utils.setTextColor("red"), end="")
            print(f"[ERROR] An error occurred: {e}")
            print(utils.setTextColor("white"), end="")

        return data
