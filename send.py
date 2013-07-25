import sys
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dev = sys.argv[1]
s.setsockopt(socket.SOL_SOCKET, 25, dev)
s.sendto(sys.argv[2], ("192.168.0.1", 1))
