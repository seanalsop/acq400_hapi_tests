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
    if args.trg != "notouch":
        uut.s1.trg = "1,%d,%d" % (0 if args.trg.split(',')[0] == 'ext' else 1,
                                  0 if args.trg.split(',')[1] == 'falling' else 1)

    c_args = args.clk.split(',')
    if len(c_args) > 1:
        c_args[1] = intSI(c_args[1])
        if len(c_args) > 2:
            c_args[2] = intSI(c_args[2])
    # worktodo .. set clock 
    uut.s0.run0 = uut.s0.sites

    for s in args.sim.split(','):
        print("hello s {}".format(s))

    if str(3) in args.sim.split(','):
        print("in")
    else:
        print("NOT IN")

    sim_sites = {}
    if args.sim != "nosim":
        sim_sites = [ int(s) for s in args.sim.split(',')]

    for site in uut.modules:
        sim = '1' if site in sim_sites else '0'
        uut.svc['s%s' % (site)].simulate = sim
        print("site {} sim {}".format(site, sim))


def init_comms(uut, args):
    if args.commsA != "none":
        uut.cA.spad = 0
        uut.cA.aggregator = "sites=%s" % (uut.s0.sites if args.commsA == 'all' else args.commsA)
    if args.commsB != "none":
        uut.cB.spad = 0
        uut.cB.aggregator = "sites=%s" % (uut.s0.sites if args.commsB == 'all' else args.commsB)

def init_work(uut, args):
    print("init_work")

def start_shot(uut, args):    
    uut.s0.streamtonowhered = "start"


def stop_shot(uut):
    print("stop_shot")
    uut.s0.streamtonowhered = "stop"

def run_shot(args):    
    uut = acq400_hapi.Acq2106(args.uut[0])

    config_shot(uut, args)
    init_comms(uut, args)
    init_work(uut, args)
    try:
        start_shot(uut, args)
        for ts in range(0, int(args.secs)):
            sys.stdout.write("Time ... %8d / %8d\r" % (ts, int(args.secs)))
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    stop_shot(uut)



def run_main():
    parser = argparse.ArgumentParser(description='configure acq2106 High Throughput Stream')    
    parser.add_argument('--post', default=0, help="capture samples [default:0 inifinity]")
    parser.add_argument('--secs', default=999999, help="capture seconds [default:0 inifinity]")
    parser.add_argument('--clk', default="int 50000000", help='clk "int|ext,SR,[CR]"')
    parser.add_argument('--trg', default="int", help='trg "int|ext,rising|falling"')
    parser.add_argument('--sim', default="nosim", help='list of sites to run in simulate mode')
    parser.add_argument('--commsA', default="all", help='custom list of sites for commsA')
    parser.add_argument('--commsB', default="none", help='custom list of sites for commsB')
    parser.add_argument('uut', nargs='+', help="uut ")
    run_shot(parser.parse_args())



# execution starts here

if __name__ == '__main__':
    run_main()

