#!/usr/bin/env python

import signal
import sys
import threading
import time
from acq400_hapi import *

uuts = [ 
            Acq400("10.12.132.22")
#            , Acq400("10.12.132.12")
        ]

def run_shot():
    for u in uuts:
        u.statmon.stopped.clear()
        u.statmon.armed.clear()

    tp = [ threading.Thread(target=u.statmon.wait_stopped) for u in uuts]

#    print("ENTER TP LOOP")

    for t in tp:
        t.setDaemon(True)
        t.start()
#        print("tp start %s" % (t.name))

#    print("FINISHED TP LOOP")
    ta = [threading.Thread(target=u.statmon.wait_armed) for u in uuts]

    for t in ta:
        t.setDaemon(True)
        t.start()
 #       print("tp start %s" % (t.name))
   
#    cc = raw_input("now set arm")
#    for t in ta:
#        print("ta %s state %d" % (t, t.is_alive()))

    print("let's go")
 
    for u in uuts:
        print("set_arm %s" % (u.uut))
        u.s0.set_arm = 1

    for t in ta:
        t.join()
    print("is armed, join done")

#    cc = raw_input("hit return for soft_trigger %s" % (uuts[0].uut))
    print("soft_trigger %s" % (uuts[0].uut))
    uuts[0].s0.soft_trigger = 1
#    cc = raw_input("CR to continue")

    print("join tp")
    for t in tp:
        t.join()

    for u in uuts:
        print("SHOT COMPLETE uut:%s shot:%s" % (u.uut, u.s1.shot))

def sleep(secs):
    print("sleep(%.2f)" % (secs))
    time.sleep(secs)
    
# execution starts here

class ExitCommand(Exception):
    pass


def signal_handler(signal, frame):
    raise ExitCommand()


signal.signal(signal.SIGINT, signal_handler)
for u in uuts:
    u.s1.shot = 0

for u in uuts:
    print("Kickoff %s shot %s" % (u.uut, u.s1.shot))

try:
    while True:
        run_shot()
        sleep(0.5)
except ExitCommand:
    print("ExitCommand raised and caught")
finally:
    print("Finally, going down")




