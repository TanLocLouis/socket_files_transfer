import utils
import clientCore
import signal
import sys

#-----------------SETTINGS UP CONSOLE-----------------#
screenWidth = 80
screenHeigh = 25

TITLE = "SOCKET FILES TRANSFER";
filename = "input.txt"


utils.clearScreen()
print(utils.setTextColor('green'))
print(screenWidth * "-")
print(TITLE)
print(screenWidth * "-", end="")
print(utils.setTextColor('white'))

print("0. Exit")
print("1. Download file from server with input.txt")

# Processing users' choice
print()
print("Choose your option: ", end="")
choice = int(input())

if choice == 0:
    print("Exiting...")
if choice == 1:
    print("Downloading file from server with input.txt")
    c1 = clientCore.SocketClient()
    c1.connect_to_server(filename)
    
#Press Ctrl + C to exit
def handle_exit(signum, frame):
    print("\nCtrl+C detected. Exiting program...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

#-----------------SETTINGS UP CONSOLE-----------------#

