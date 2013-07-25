#!/usr/bin/python

#import socket
#
#s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
#s.bind(('hdlc0',0))
##s.setsockopt(socket.SOL_SOCKET, 25, "hdlc0")
#s.send(b'\000\001\002\003')
##s.bind(("192.168.0.1", 8080))
#while True:
#	print s.recv(65565)

import sys
import pcap
import array

p = pcap.pcapObject()
dev = sys.argv[1]
net, mask = pcap.lookupnet(dev)
p.open_live(dev, 1600, 0, 100)
p.setfilter("udp", 0, 0)

def print_packet(pktlen, data, timestamp):
	print data[32:] 
	sys.exit(0)

try:
	while 1:
		p.dispatch(1, print_packet)
except KeyboardInterrupt:
	print '%d packets received, %d packets dropped, %d packets dropped by interface' % p.stats()
