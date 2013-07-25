#!/bin/bash

/etc/init.d/dahdi stop
modprobe dahdi
sleep 1
dahdi_cfg -vvf
python /usr/src/mytools/dahdi_test/fxs_server.py 8000 49 & sleep 1 ; python /usr/src/mytools/dahdi_test/analog_sig_test.py -vv http://localhost:8000 51
