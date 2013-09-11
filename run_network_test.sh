#!/bin/sh
#
# run_network_test.sh  -  Ensures that DAHDI operates in a basic HDLC mode.
#
# This test will setup two dynamic local spans in HDLC mode, and then configure
# them to be opposite sides of a Point to Point link.  It will then send write a
# random packet on one end and check that the data was received on the other
# end.
#
# This test users libpcap in order to "listen" on one end of the link.
#
set -e

/etc/init.d/dahdi stop
modprobe hdlc_cisco
modprobe --first-time dahdi
sleep 1
dahdi_cfg -c /vagrant/dahdi_nethdlc.conf
/usr/src/dahdi-tools/sethdlc hdlc0 cisco
/usr/src/dahdi-tools/sethdlc hdlc1 cisco
/sbin/ifconfig hdlc0 192.168.0.1 pointopoint 192.168.0.2
/sbin/ifconfig hdlc1 192.168.0.2 pointopoint 192.168.0.1
od -t x4 -N 4 /dev/urandom > /tmp/test.txt
python /vagrant/listen.py hdlc0 > /tmp/new.txt &
sleep 1
python /vagrant/send.py hdlc1 "$(cat /tmp/test.txt)"
wait
diff /tmp/test.txt /tmp/new.txt
if [ $? -ne 0 ]; then
	echo "TEST FAIL"
else
	echo "TEST PASS"
fi
