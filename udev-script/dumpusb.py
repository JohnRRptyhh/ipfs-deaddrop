#!/usr/bin/env python

import os
import sys
import time
import glob
import subprocess
import threading
import signal
import json

from datetime import datetime

#### CONFIGURATION ####

AUTOMOUNT_DIR = '/automount'
DUMP_DIR = '/dump'
QRCODE_PAGE_URL = 'http://ipfs.io/ipfs/QmawVyLHjR8qmYXd5GZgKUPhvnzDsJko1g6H8mkHzLKNij'
#URLOPEN_CMD = "sudo -u siri -i luakit --display=:0.0"
URLOPEN_CMD = "echo mosquitto_pub -h 10.0.1.17 -t siri/donotopen -m"
IPFS_USER = 'ipfs'
STATEFILE = '/var/www/siri-data-rescue/www/deaddrop.json'
PERCENTFILE = '/tmp/percent.txt'
PERCENT_URL = 'http://siri.cbrp3.c-base.org/status'
PROGRESS_HTML_URL = 'http://localhost/dumpusb.html'

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
            percent = (curr / float(total)) * 100.0
            int_percent = int(percent)
	    if int_percent == 100:
                int_percent = 99
            with open(STATEFILE, mode="w") as f:
                json.dump({"changed": datetime.utcnow().isoformat(), "percent": int_percent, "message": "Copying file(s) ...", "qrcode": None}, f)
            with open(PERCENTFILE, mode="w") as f:
                f.write('%d\n' % int_percent)
                
            time.sleep(0.5)

def main():
    with open(PERCENTFILE, mode="w") as f:
        f.write('%d\n' % 0)
    with open(STATEFILE, mode="w") as f:
        json.dump({"changed": datetime.utcnow().isoformat(), "percent": 0, "message": "Copying file(s) ...", "qrcode": None}, f)
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
        
        # Show status page
        msg = '%s "%s"' % (URLOPEN_CMD, PERCENT_URL)
        print msg
        subprocess.call(msg.split())
        
        meter = ProgressMeter(dumpdir)
        meter.start()
        command = "rsync --one-file-system -r %s/* %s" % (AUTOMOUNT_DIR, dumpdir)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
   
        process.wait()
        meter.on_finished()        
        meter.join()
        exitCode = process.returncode

        subprocess.call(['umount', AUTOMOUNT_DIR])
        
        with open(STATEFILE, mode="w") as f:
            json.dump({"changed": datetime.utcnow().isoformat(), "percent": 99, "message": "Publishing on IPFS ...", "qrcode": None}, f)
            
        with open(PERCENTFILE, mode="w") as f:
            f.write('%d\n' % 100)
    
        if (exitCode == 0):
            command="sudo -u %s -i -- ipfs add -q -r -w %s/* | tail -n 1" % ('ipfs', dumpdir)
            print(command)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, err = process.communicate()
            rc = process.returncode
            ipfs_hash = output.split()[0]
            qrcode = 'http://ipfs.io/ipfs/%s/' % ipfs_hash
            msg = '%s "%s?%s"' % (URLOPEN_CMD, QRCODE_PAGE_URL, qrcode)
            print msg
            with open(STATEFILE, mode="w") as f:
                json.dump({"changed": datetime.utcnow().isoformat(), "percent": 100, "message": "Success!", "qrcode": qrcode}, f)
            #subprocess.call(msg.split())
            return output
        else:
            with open(STATEFILE, mode="w") as f:
                json.dump({"changed": datetime.utcnow().isoformat(),"percent": 100, "message": "There was an error! Please try again.", "qrcode": None}, f)
            raise Exception(command, exitCode, output)
main()
