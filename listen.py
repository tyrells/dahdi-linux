#!/usr/bin/python

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
