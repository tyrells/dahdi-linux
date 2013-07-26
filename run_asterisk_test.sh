#!/bin/bash
asterisk -rx 'core stop now'
set -e
/etc/init.d/dahdi stop
modprobe --first-time dahdi
dahdi_cfg -vvf
sleep 1
asterisk -C /vagrant/asterisk_configs/asterisk.conf
sleep 1
asterisk -rx 'core waitfullybooted'
rm -f -r /tmp/dtmf.txt
asterisk -rx 'channel originate dahdi/51/5550 extension 5555@read_dtmf'
asterisk -rx 'core stop when convenient'
cat /tmp/dtmf.txt
