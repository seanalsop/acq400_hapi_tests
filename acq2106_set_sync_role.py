#!/usr/bin/env python

""" 
acq2106_set_sync_role master [slave1 ... slaveN]
"""

import argparse
import acq400_hapi


def run_main(parser):
    uuts = [ acq400_hapi.Acq400(addr) for addr in parser.uuts ]      
    
    role = "master"
    
    for uut in uuts:
        uut.set_sync_routing(role)
        role = "slave"

# execution starts here

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='acq2106_set_sync_role')
    parser.add_argument('uuts', nargs='+', help="uut pairs: m1,m2 [s1,s2 ...]")
    run_main(parser.parse_args())


