import socketserver
import utils
import serverCore
import sys
import signal

s1 = serverCore.SocketServer()
s1.createServer()

# Close program when transfer file DONE
def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
print('Press Ctrl+C')
signal.pause()
