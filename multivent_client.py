#!/usr/local/bin/python
# UUT is running continuous pre/post snapshots
# subscribe to the snapshots and save all the data.

import threading
import epics
import argparse
import time

NCHAN=16

class Uut:
    def on_update(self, **kws):
        print("{} {}".format(kws['pvname'], kws['value']))
        
    def monitor(self):
        updates = epics.PV(self.name + ":1:AI:WF:01:UPDATES", auto_monitor=True, callback=self.on_update)
        
    def __init__(self, _name):
        self.name = _name
        threading.Thread(target=self.monitor).start()
        

def multivent(args):
    uuts = [Uut(_name) for _name in args.uuts]
    while True:
        time.sleep(0.5)
    
def run_main():
    parser = argparse.ArgumentParser(description='acq400 multivent')
    parser.add_argument('uuts', nargs='+', help="uut names")
    multivent(parser.parse_args())

# execution starts here
if __name__ == '__main__':
    run_main()
