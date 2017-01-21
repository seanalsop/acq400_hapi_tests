#!/usr/bin/env python

import signal
import sys
import threading
import time
from acq400_hapi import *

uuts = [  ]

def run_shot():
    for u in uuts:
        u.statmon.stopped.clear()
        u.statmon.armed.clear()

    tp = [ threading.Thread(target=u.statmon.wait_stopped) for u in uuts]

    for t in tp:
        t.setDaemon(True)
        t.start()

    ta = [threading.Thread(target=u.statmon.wait_armed) for u in uuts]

    for t in ta:
        t.setDaemon(True)
        t.start()

    for u in uuts:
        print("%s set_arm" % (u.uut))
        u.s0.set_arm = 1

    for t in ta:
        t.join()

    print("%s soft_trigger" % (uuts[0].uut))
    uuts[0].s0.soft_trigger = 1

    for t in tp:
        t.join()

    for u in uuts:
        print("%s SHOT COMPLETE shot:%s" % (u.uut, u.s1.shot))

def sleep(secs):
    print("sleep(%.2f)" % (secs))
    time.sleep(secs)

class ExitCommand(Exception):
    pass
    
    
def signal_handler(signal, frame):
    raise ExitCommand()
    
# execution starts here



if __name__ == '__main__':
    SERVER_ADDRESS = '10.12.132.22'
    if len(sys.argv) > 1:
        uuts = []
        for addr in sys.argv[1:]:            
            uuts.append(Acq400(addr))
    else:
        uuts.append(Acq400("10.12.132.22"))

    
signal.signal(signal.SIGINT, signal_handler)

for u in uuts:
    u.s1.shot = 0
    print("%s Kickoff shot %s" % (u.uut, u.s1.shot))

try:
    while True:
        run_shot()
        sleep(1.0)
except ExitCommand:
    print("ExitCommand raised and caught")
finally:
    print("Finally, going down")




