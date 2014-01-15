#!/bin/bash

/etc/init.d/dahdi stop
modprobe dahdi auto_assign_spans=1
sleep 1
dahdi_cfg -c /vagrant/dahdi.conf
python /usr/src/mytools/dahdi_test/fxs_server.py 8000 49 & sleep 1 ; python /usr/src/mytools/dahdi_test/digital_rbs_sig_test.py -vv http://localhost:8000 51
