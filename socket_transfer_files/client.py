import utils
import clientCore
import signal
import sys
import clientCoreUDP


def main():
    # -----------------SETTINGS UP CONSOLE-----------------#
    screenWidth = 80
    screenHeigh = 25

    TITLE = "SOCKET FILES TRANSFER"
    filename = "input.txt"

    utils.clearScreen()
    print(utils.setTextColor("green"))
    print(screenWidth * "-")
    print(
        "|"
        + utils.setTextColor("cyan")
        + " " * ((screenWidth - len(TITLE)) // 2 - 1)
        + TITLE
        + " " * ((screenWidth - len(TITLE)) // 2 - 1)
        + utils.setTextColor("green")
        + "|"
    )
    print(screenWidth * "-", end="")
    print(utils.setTextColor("white"))

    server_ip = input("Enter server IP: ")
    download_dir = input("Enter download path: ")
    
    print("0. Exit")
    print("1. Download file from server with input.txt with TCP")
    print("2. Download file from server with input.txt with UDP")

    # Processing users' choice
    print("Choose your option: ", end="")
    choice = int(input())

    # Select choice from menu
    if choice == 0:
        print("Exiting...")
    if choice == 1:
        print("Downloading file from server with input.txt with TCP")
        c1 = clientCore.SocketClient()
        c1.connect_to_server(filename, download_dir, server_ip)
    if choice == 2:
        print("Downloading file from server with input.txt with UDP")
        c2 = clientCoreUDP.SocketClientUDP()
        c2.connect_to_server(filename, download_dir, server_ip)
    # Press Ctrl + C to exit

    input("Press Ctrl + C to exit program")
    def handle_exit(signum, frame):
        print("\nCtrl+C detected. Exiting program...")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    # -----------------SETTINGS UP CONSOLE-----------------#

if __name__ == "__main__":
    main()
