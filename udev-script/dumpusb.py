#!/usr/bin/env python
import os
import sys
import time
import glob
import subprocess
import threading
import signal

#### CONFIGURATION ####

AUTOMOUNT_DIR = '/automount'
DUMP_DIR = '/dump'
QRCODE_PAGE_URL = 'http://siri.cbrp3.c-base.org:8080/ipfs/QmUzER8RFyFMKfcE5WKcCWdK1pFXJMVKoCzeHEw2XWpibA/'
URLOPEN_CMD = "mosquitto_pub -h 10.0.1.17 -t siri/open -m"
IPFS_USER = 'ipfs'

#### END CONFIGURATION ####

# Grace period for USB and udev to become ready

dumpdir = os.path.join(DUMP_DIR, time.strftime('%Y%m%d%H%M%S'))

device_name = ''

print(sys.argv)
if len(sys.argv) > 1: 
    device_name = sys.argv[1]
else:
    print("ERROR: No device name given, usage example: dumpusb.py /dev/sdX")
    exit(1)


class ProgressMeter(threading.Thread):
    def __init__(self, dumpdir):
        self.stdout = None
        self.stderr = None
        self.mylock = threading.RLock()
        self.ongoing = True
        self.dumpdir = dumpdir
        threading.Thread.__init__(self)

    def do_du(self, directory):
        p = subprocess.Popen(['du', '-s', directory], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        rc = p.returncode
        bla = output.split()[0]
        return float(bla)

    def is_ongoing(self):
        with self.mylock:
            return self.ongoing

    def on_finished(self):
        with self.mylock:
            self.ongoing = False

    def run(self):
        total = self.do_du(AUTOMOUNT_DIR)
        while self.is_ongoing():
            curr = self.do_du(dumpdir)
            print curr / total
            time.sleep(0.5)


def main():
    meter = None
    def signal_handler(signal, frame):
        print 'You pressed Ctrl+C!'
        if meter != None:
            meter.on_finished()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print("5 seconds grace period ... please wait!")
    time.sleep(0.2)
    print("glob:", glob.glob('%s?' % device_name))
    os.makedirs(dumpdir)
    for partition in sorted(glob.glob('%s?' % device_name)):
        print("Importing files from partition %s ..." % partition)
        subprocess.call(['mount', '-o', 'ro', partition, AUTOMOUNT_DIR])
        
        meter = ProgressMeter(dumpdir)
        meter.start()
        command = "rsync -r %s/* %s" % (AUTOMOUNT_DIR, dumpdir)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
   
        process.wait()
        meter.on_finished()        
        meter.join()
        exitCode = process.returncode

        subprocess.call(['umount', AUTOMOUNT_DIR])
    
        if (exitCode == 0):
            command="sudo -u %s -i -- ipfs add -q -r -w %s/* | tail -n 1" % ('ipfs', dumpdir)
            print(command)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, err = process.communicate()
            print("HASH")
            print(output)
	    msg = "%s %s/?http://siri.cbrp3.c-base.org:8080/ipfs/%s/" % (URLOPEN_CMD, QRCODE_PAGE_URL, output)
	    print(msg)
            rc = process.returncode
            return output
        else:
            raise Exception(command, exitCode, output)
main()

#do
#  mkdir -p $AUTOMOUNT_DIR || break
#  mount $partition $AUTOMOUNT_DIR || break
#  mkdir -p $dumpdir/`basename $partition` || break
#  destdir=$dumpdir/`basename $partition`
#  cp -r /automount/* $destdir
#  umount /automount
#
#  # The last of the hashes that the ipfs-add command generates is the one of the
#  # wrapping directory
#  hash=`sudo -u ${IPFS_USER} -i -- ipfs add -q -r -w ${destdir}/* | tail -n 1`
#  $URLOPEN_CMD "${QRCODE_PAGE_URL}/?http://siri.cbrp3.c-base.org:8080/ipfs/${hash}/"
#done
