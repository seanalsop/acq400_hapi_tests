#!/usr/bin/env python

""" capture upload test
    acq1001_capplot UUT1 [UUT2 ..]
    where UUT1 is the ip-address or host name of first uut
    example test client runs captures in a loop on one or more uuts
    
    pre-requisite: UUT's are configured and ready to make a transient
    capture 
    eg clk is running. soft trg enabled
    eg transient length set.
    
    runs one capture, uploads the data and plots with matplotlib
    tested with 2 x 8 channels UUT's (ACQ1014)
    matplot will get very congested with more channels.
    this is really meant as a demonstration of capture, load to numpy,
    it's not really intended as a scope UI.
"""

import sys
import acq400_hapi
import numpy as np
import matplotlib.pyplot as plt

def run_main():
    uuts = [  ]        
    if len(sys.argv) > 1:        
        for addr in sys.argv[1:]:            
            uuts.append(acq400_hapi.Acq400(addr))
    else:
        print("USAGE: acq1001_caploop UUT1 [UUT2 ..]")
        sys.exit(1)        

    acq400_hapi.cleanup.init()

    shot_controller = acq400_hapi.ShotController(uuts)

    try:        
        shot_controller.run_shot(soft_trigger=True)

        chx = [u.read_channels() for u in uuts]
        
        nsam = uuts[0].post_samples()
        nchan = uuts[0].nchan()
        ncol = len(uuts)
        
# plot ex: 2 x 8 ncol=2 nchan=8
# U1 U2      FIG
# 11 21      1  2
# 12 22      3  4
# 13 23
# ...
# 18 28     15 16
        for col in range(ncol):
            for chn in range(0,nchan):
                fignum = 1 + col + chn*ncol
                plt.subplot(nchan, ncol, fignum)                
                plt.plot(chx[col][chn])
                        
        plt.show()
            
    except acq400_hapi.cleanup.ExitCommand:
        print("ExitCommand raised and caught")
    finally:
        print("Finally, going down")

# execution starts here

if __name__ == '__main__':
    run_main()




