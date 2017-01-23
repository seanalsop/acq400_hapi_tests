#!/usr/bin/env python

""" configure transient 
    acq1014_configure_transient UUT1 UUT2 [NPOST] [trigger=int|ext|ext2]
"""

import sys
import acq400_hapi


def configure_shot(uuts, npost, trigger):
    for u in uuts:
        print("uut:%s" % u.uut)
        u.s0.trace = 1;
        u.s0.transient = '"POST=%d"' % int(npost)
        u.s0.acq1014_select_trg_src = trigger
        u.s0.trace = 0

def run_main():
    uuts = [  ]        
    npost = 100000
    trigger = 'int'
    if len(sys.argv) > 2:       
        for addr in sys.argv[1:3]: 
            print("uut:%s" % addr)
            uuts.append(acq400_hapi.Acq400(addr))
        if len(sys.argv) > 3:
            npost = int(sys.argv[3])
        if len(sys.argv) > 4:
            trigger = sys.argv[4]
    else:
        print("USAGE: acq1014_configure_transient UUT1 UUT2 [NPOST] [trigger=]")
        sys.exit(1)        

    configure_shot(uuts, npost, trigger)


# execution starts here

if __name__ == '__main__':
    run_main()

