#!/usr/bin/python
#
# This script will make sure the virtual machine is properly setup for running
# the dahdi_dynamic local span tests.
#
import sys
import subprocess
import os
import time
import cStringIO as StringIO

def call(command):
    return subprocess.call(command, shell=True)

def call_output(command):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()[0].strip()

def setup_dahdi_linux():
    if os.path.exists("/usr/src/dahdi-tools"):
        os.chdir("/usr/src/dahdi-tools")
        call("git fetch -q; git reset -q --hard origin/master")
        source_version = call_output("build_tools/make_version .")
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

def setup_my_tools():
    if os.path.exists("/usr/src/mytools"):
        os.chdir("/usr/src/mytools")
        call("git fetch -q; git reset -q --hard origin/master")
    else:
        os.chdir("/usr/src")
        call("git clone git://git.digium.internal/team/sruffell/mytools")

def setup_libpri():
    if os.path.exists("/usr/src/libpri-1.4.14"):
        return
    os.chdir("/usr/src")
    call("svn co http://svn.asterisk.org/svn/libpri/tags/1.4.14 libpri-1.4.14")
    os.chdir("/usr/src/libpri-1.4.14")
    call("make; make install")
    
def setup_asterisk():
    if os.path.exists("/usr/src/asterisk-11.5.0"):
        return
    os.chdir("/usr/src")
    call("svn co http://svn.asterisk.org/svn/asterisk/tags/11.5.0 asterisk-11.5.0")
    os.chdir("/usr/src/asterisk-11.5.0")
    if call("/usr/src/asterisk-11.5.0/contrib/scripts/install_prereq install"):
        raise Exception("Failed to install asterisk prereqs")
    call("./configure; make; make install")

def apt_update():
    # Let's use the digium internal repository.
    open("/etc/apt/sources.list", "w").write("""deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise main restricted
    deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise-updates main restricted
    deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise universe
    deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise-updates universe
    deb http://10.24.17.167:3142/journey.digium.internal/ubuntu/ precise-backports main restricted
    deb http://10.24.17.167:3142/journey.digium.internal/ubuntu precise-security main restricted
    deb http://10.24.17.167:3142/journey.digium.internal/ubuntu precise-security universe
    """)

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
            version = line.split('-', 1)[1].split('g',1)
            return version[-1].strip()

    raise Exception("Huh? No DAHDI Tools Version printed?")

def disable_fsck():
    new_fstab = StringIO.StringIO()
    fstab = open("/etc/fstab", "r")
    for line in fstab:
        if line.startswith('#'):
            new_fstab.write(line)
            continue
        parts = line.split()
        if len(parts) == 6:
            parts[5] = "0"
        new_fstab.write(" ".join(parts) + "\n")
    fstab.close()
    open("/etc/fstab", "w").write(new_fstab.getvalue())

def update_kernel_command_line():
    new_grub = StringIO.StringIO()
    grub = open("/etc/default/grub", "r")
    for line in grub:
        if not line.startswith("GRUB_CMDLINE_LINUX"):
            new_grub.write(line)
            continue
        new_grub.write('GRUB_CMDLINE_LINUX="console=ttyS0,115200n81"\n')
    grub.close()
    open("/etc/default/grub", "w").write(new_grub.getvalue())
    cmdline = open("/proc/cmdline").read()
    if -1 == cmdline.find("console=ttyS0"):
        call("update-grub")

def main():
    apt_update()
    call("apt-get install -y build-essential tig subversion git vim python-libpcap debconf-utils")
    call("apt-get install -y gcc libncurses-dev libnewt-dev libtool make linux-headers-$(uname -r)")
    call('echo "grub-pc grub-pc/install_devices multiselect /dev/sda" | debconf-set-selections')
    call('echo "libvpb0 libvpb0/countrycode string  1" | debconf-set-selections')
    call("apt-get -y dist-upgrade")
    
    setup_dahdi_linux()
    setup_libpri()
    setup_asterisk()
    setup_my_tools()
    disable_fsck()
    update_kernel_command_line()
    
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
echocanceller=mg2,49-50
dynamic=loc,2:3,2,0
fxsks=51-52
echocanceller=mg2,51-52
loadzone        = us
defaultzone     = us
""")

    print "*******************************************************************************"
    print "Please run 'vagrant halt' followed by 'vagrant up --no-provision' before       "
    print "using virtual machine."
    print "*******************************************************************************"
    return 0

if "__main__" == __name__:
    print __name__
    sys.exit(main())
