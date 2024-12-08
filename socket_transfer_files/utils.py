import os

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
