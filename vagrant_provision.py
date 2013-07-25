#!/usr/bin/python
#
# This script will make sure the virtual machine is properly setup for running
# the dahdi_dynamic local span tests.
#
import sys
import subprocess
import os
import time

def call(command):
    return subprocess.call(command, shell=True)

def call_output(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()[0].strip()

def apt_update():
    # This ensures that we do not run apt-get update any more frequently than
    # once every 24 hours
    def _apt_update():
        call("mkdir -p /var/lib/vagrant")
        call("apt-get update -y")
        open("/var/lib/vagrant/last_update", "w+").write(str(time.time()))
    try:
        last_update = float(open("/var/lib/vagrant/last_update", "r").read().strip())
        if not ((time.time() - last_update) < (3600*24)):
            _apt_update()
    except Exception as e:
        _apt_update()

def dahdi_tools_installed_version():
    if not os.path.exists("/usr/sbin/dahdi_cfg"):
        return "0000000" 
    p = subprocess.Popen("/usr/sbin/dahdi_cfg -v", shell=True,
                     stdout=open("/dev/null", "w+"), stderr=subprocess.PIPE)
    p.wait()

    for line in p.stderr:
        line = line.strip()
        if line.startswith("DAHDI Tools Version"):
            return [x.strip() for x in line.split('-', 1)][1].split('g',1)[1]

    raise Exception("Huh? No DAHDI Tools Version printed?")

# Let's use the digium internal repository.
open("/etc/apt/sources.list", "w").write("""deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise main restricted
deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise-updates main restricted
deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise universe
deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise-updates universe
deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise-backports main restricted
deb http://10.24.17.167:3142/journey.digium.internal/ubuntu precise-security main restricted
deb http://10.24.17.167:3142/journey.digium.internal/ubuntu precise-security universe
""")

apt_update()
call("apt-get install -y build-essential tig git vim python-libpcap")
call("apt-get install -y gcc libncurses-dev libnewt-dev libtool make linux-headers-$(uname -r)")
call('echo "grub-pc grub-pc/install_devices multiselect /dev/sda" | debconf-set-selections')
call("apt-get -y dist-upgrade")

if os.path.exists("/usr/src/dahdi-tools"):
    os.chdir("/usr/src/dahdi-tools")
    call("git fetch -q; git reset -q --hard origin/master")
    source_version = call_output("git log -1 --oneline | cut -f 1 -d \ ")
    installed_version = dahdi_tools_installed_version()
    if installed_version != source_version:
        call("./configure; make; make install; make config")
else:
    # Dahdi linux needs to be installed in order to build dahdi_tools
    if os.path.exists("/usr/src/dahdi-linux"):
        os.chdir("/usr/src/dahdi-linux")
        call("git fetch -q; git reset -q --hard origin/master")
    else:
        os.chdir("/usr/src")
        call("git clone git://git.asterisk.org/dahdi/linux dahdi-linux")
        os.chdir("/usr/src/dahdi-linux")
    call("make install")

    os.chdir("/usr/src")
    call("git clone git://git.asterisk.org/dahdi/tools dahdi-tools")
    os.chdir("/usr/src/dahdi-tools")
    call("./configure; make; make install; make config")

if os.path.exists("/usr/src/mytools"):
    os.chdir("/usr/src/mytools")
    call("git fetch -q; git reset -q --hard origin/master")
else:
    os.chdir("/usr/src")
    call("git clone git://git.digium.internal/team/sruffell/mytools")


call("mkdir -p /etc/dahdi/")
open("/etc/dahdi/system.conf", "w").write("""dynamic=loc,1:0,24,0
bchan=1-23
dchan=24
echocanceller=mg2,1-23
dynamic=loc,1:1,24,0
bchan=25-47
dchan=48
echocanceller=mg2,1-23
dynamic=loc,2:2,2,0
fxoks=49-50
dynamic=loc,2:3,2,0
fxsks=51-52
loadzone        = us
defaultzone     = us
""")

print "*******************************************************************************"
print "Please run 'vagrant halt' followed by 'vagrant up --no-provision' before       "
print "using virtual machine."
print "*******************************************************************************"
