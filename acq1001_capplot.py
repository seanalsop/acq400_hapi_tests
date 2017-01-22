#!/usr/bin/env python

import signal
import sys
import time
import acq400_hapi
import numpy as np
import matplotlib.pyplot as plt


def sleep(secs):
    print("sleep(%.2f)" % (secs))
    time.sleep(secs)

class ExitCommand(Exception):
    pass
    
    
def signal_handler(signal, frame):
    raise ExitCommand()
    


def run_main():
    uuts = [  ]    
    SERVER_ADDRESS = '10.12.132.22'
    if len(sys.argv) > 1:
        uuts = []
        for addr in sys.argv[1:]:            
            uuts.append(acq400_hapi.Acq400(addr))
    else:
        uuts.append(acq400_hapi.Acq400("10.12.132.22"))

    
    signal.signal(signal.SIGINT, signal_handler)

    shot_controller = acq400_hapi.ShotController(uuts)

    try:        
        shot_controller.run_shot(soft_trigger=True)        
        ch01 = uuts[0].read_chan(1)
        plt.plot(ch01)
        plt.show()
            
    except ExitCommand:
        print("ExitCommand raised and caught")
    finally:
        print("Finally, going down")

# execution starts here
    

if __name__ == '__main__':
    run_main()




