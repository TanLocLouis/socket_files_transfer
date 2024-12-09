import os
import socket

# -----------------------UTILS FUNCTIONS FOR CONSOLE-----------------------#
def clearScreen():
    os.system("cls")


def gotoxy(x, y):
    print("\033[%d;%dH" % (x, y), end="")


def setTextColor(color):
    if color == "red":
        return "\033[91m"
    elif color == "green":
        return "\033[92m"
    elif color == "yellow":
        return "\033[93m"
    elif color == "blue":
        return "\033[94m"
    elif color == "purple":
        return "\033[95m"
    elif color == "cyan":
        return "\033[96m"
    elif color == "white":
        return "\033[97m"
    else:
        return "\033[0m"


# -----------------------UTILS FUNCTIONS FOR CONSOLE-----------------------#


def get_file_size(filename):
    """
    Get the size of the file in bytes.
    """
    return os.path.getsize(filename)


def check_file_exist(filename):
    """
    Check if the file exists.
    """
    return os.path.exists(filename)


def count_files_with_prefix(directory, prefix):
    count = 0
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            count += 1
    return count

def find_free_port(HOST):
    """
    Find a free port on the server.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]

def list_all_file_in_directory(directory):
    """
    List all files in the current directory.
    """

    file_list = []
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                file_list.append((file_path, file_size))
    except Exception as e:
        print(f"Error: {e}")
        
    return file_list

def standardize_str(s, n):
    while len(s) < n:
        s += " "
    return s

