#!/bin/bash
asterisk -rx 'core stop now' > /dev/null 2>&1 
set -e
/etc/init.d/dahdi stop
modprobe --first-time dahdi auto_assign_spans=1
dahdi_cfg -c /vagrant/dahdi.conf
sleep 1
asterisk -C /vagrant/asterisk_configs/asterisk.conf
sleep 1
asterisk -rx 'core waitfullybooted'
rm -f -r /tmp/dtmf.txt
asterisk -rx 'channel originate dahdi/51/5550 extension 5555@read_dtmf'
asterisk -rx 'core stop when convenient'
RESULTS=$(cat /tmp/dtmf.txt | cut -f 1 -d \ | uniq)
if [[ $RESULTS == "PASS!" ]]; then
	echo "PASS"
	exit 0
else
	echo "FAIL"
	exit 1
fi
