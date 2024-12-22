import serverCore
import serverCoreUDP

def main():
    print("1. TCP Server")
    print("2. UDP Server")
    
    print("Choose your option: ", end="")
    choice = int(input())

    if choice == 1:
        s1 = serverCore.SocketServer()
        s1.create_server()
    if choice == 2:
        s2 = serverCoreUDP.SocketServerUDP()
        s2.create_server()

if __name__ == "__main__":
    main()
    
