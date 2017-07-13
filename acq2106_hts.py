#!/usr/bin/env python

""" acq2106_hts
    control High Throughput Streaming on local SFP/AFHBA
    replaces AFHBA404/scripts/hts-test-harness-*
"""

import sys
import acq400_hapi
from acq400_hapi import intSI as intSI
import argparse
import time


def config_shot(uut, args):
    uut.s1.trg = "1,%d,%d" % (0 if args.trg.split(' ')[0] == 'ext' else 1,
                              0 if args.trg.split(' ')[1] == 'falling' else 1)

    c_args = args.clk.split(' ')
    if len(c_args) > 1:
        c_args[1] = intSI(c_args[1])
        if len(c_args) > 2:
            c_args[2] = intSI(c_args[2])
    # worktodo .. set clock 
    uut.s0.run0 = uut.s0.sites

def init_comms(uut):
    uut.cA.spad = 0
    uut.cA.aggregator = "sites=%s" % (uut.s0.sites)

def init_work(uut, args):
    print "init_work"

def start_shot(uut, args):    
    uut.s0.streamtonowhered = "start"


def stop_shot(uut):
    print("stop_shot")
    uut.s0.streamtonowhered = "stop"

def run_shot(args):    
    uut = acq400_hapi.Acq2106(args.uut[0])

    config_shot(uut, args)
    init_comms(uut)
    init_work(uut, args)
    try:
        start_shot(uut, args)
        time.sleep(float(args.secs))
    except KeyboardInterrupt:
        pass
    stop_shot(uut)



def run_main():
    parser = argparse.ArgumentParser(description='configure acq2106 High Throughput Stream')    
    parser.add_argument('--post', default=0, help="capture samples [default:0 inifinity]")
    parser.add_argument('--secs', default=999999, help="capture seconds [default:0 inifinity]")
    parser.add_argument('--clk', default="int 50000000", help='clk "int|ext SR [CR]"')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('uut', nargs='+', help="uut ")
    run_shot(parser.parse_args())



# execution starts here

if __name__ == '__main__':
    run_main()
