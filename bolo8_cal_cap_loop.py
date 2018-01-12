#!/usr/bin/env python
# bolo8_cal_cap_loop.py ..
# run a bolo8 calibration, store to MDSplus ODD shot
# run a bolo8 capture, store to MDSplus EVEN shot
# ASSUME : each uut has a tree of the same name


import sys
import os
import acq400_hapi
import argparse
from MDSplus import *

def odd(n):
    return n%2 == 1

def even(n):
    return n%2 == 0

def set_next_shot(args, flavour, info):
    old_shots = [Tree.getCurrent(u) for u in args.uuts]
    sn = max(old_shots) + 1
    # this is only going to run once
    while not flavour(sn):
        sn += 1
    for tree in args.uuts:
        print("Setting {} for {} to shot {}".format(tree, info, sn))
        Tree.setCurrent(tree, sn)
    return sn
    
    
def run_cal1(uut, shot):
    txt = uut.run_service(acq400_hapi.AcqPorts.BOLO8_CAL, eof="END")
    logfile = os.getenv("{}_path/cal_{}".format(uut.uut, shot), ".")
    with open(logfile, 'w') as log: 
        log.write(txt)
        
    

def run_cal(args, uuts):
    shot = set_next_shot(args, odd, "Cal")
    # hmm, running the cal serialised?. not cool, parallelize me ..
    for u in uuts:
        run_cal1(u, shot)
    
def run_capture(args, uuts):
    shot = set_next_shot(args, even, "Cap")
    for u in uuts:
        u.s0.transient = "POST={} SOFT_TRIGGER=0".format(args.post)
        u.s0.arm = '1'
        u.st_monitor.wait_armed()
        
    if args.trg == "int":
        # again, not really parallel
        for u in uuts:
            u.so.soft_trigger = '1'
            
    for u in uuts:
        u.st_monitor.wait_stopped()
        
def run_shots(args):
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts] 
    
    for shot in range(1, args.shots+1):
        run_cal(args, uuts)
        run_capture(args, uuts)

    
def run_main():
    parser = argparse.ArgumentParser(description='bolo8_cal_cap_loop')    
    parser.add_argument('--post', default=100000, help="post trigger length")
    parser.add_argument('--clk', default="int 1000000", help='clk "int|ext SR [CR]"')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('--shots', default=1, help='set number of shots [1]')
    parser.add_argument('uuts', nargs='+', help="uut list")
    run_shots(parser.parse_args())


# execution starts here

if __name__ == '__main__':
    run_main()