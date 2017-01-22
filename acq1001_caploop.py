#!/usr/bin/env python

""" capture loop test
    acq1001_caploop UUT1 [UUT2 ..]
    where UUT1 is the ip-address or host name of first uut
    example test client runs captures in a loop on one or more uuts
    
    pre-requisite: UUT's are configured and ready to make a transient
    capture 
    eg clk is running. soft trg enabled
    eg transient length set.
    
    loop continues "forever" until <CTRL-C>
"""
import signal
import sys
import time
import acq400_hapi



def sleep(secs):
    print("sleep(%.2f)" % (secs))
    time.sleep(secs)

class ExitCommand(Exception):
    pass
    
    
def signal_handler(signal, frame):
    raise ExitCommand()
    


def run_main():
    uuts = [  ]        
    if len(sys.argv) > 1:       
        for addr in sys.argv[1:]:            
            uuts.append(acq400_hapi.Acq400(addr))
    else:
        uuts.append(acq400_hapi.Acq400("10.12.132.22"))

    
    signal.signal(signal.SIGINT, signal_handler)

    shot_controller = acq400_hapi.ShotController(uuts)

    try:
        while True:
            shot_controller.run_shot(soft_trigger=True)
            sleep(1.0)            
            
    except ExitCommand:
        print("ExitCommand raised and caught")
    finally:
        print("Finally, going down")

# execution starts here

if __name__ == '__main__':
    run_main()




