#!/usr/bin/env python

""" configure and run gpg on uut
    run_gpg.py [opts] uut
"""

import sys
import acq400_hapi
import argparse


def load_stl(uut, stl):
    with open(stl, 'r') as fp: 
        uut.load_gpg(fp.read())
        
    
def soft_trigger_loop(uut):
    while True:
        key = raw_input("trigger>")
        if key == '':
            uut.s0.soft_trigger = 1
        else:
            break
    
def run_gpg(args):
    uut = acq400_hapi.Acq400(args.uut[0])
 
    if args.disable == 1:
        uut.s0.GPG_ENABLE = '0'
        return
    uut.s0.trace = 1
    if args.stl != 'none':
        load_stl(uut, args.stl)
    uut.s0.gpg_trg='1,{},1'.format(1 if args.trg == 'soft' else 0)
    uut.s0.GPG_MODE=args.mode
    uut.s0.GPG_ENABLE = '1'
    
    if args.clk == 'int':
        uut.s0.gpg_clk=0,0,0
    else:
        # clk=dX
        uut.s0.gpg_clk='1,{},1'.format(args.clk[1:])
     
    if args.trg == 'soft':
        soft_trigger_loop(uut)
    
        

def run_main():
    parser = argparse.ArgumentParser(description='run_gpg')    
    parser.add_argument('--trg', default='soft', type=str, help="trigger fp|soft")
    parser.add_argument('--clk', default='int', type=str, help='clk int|dX')
    parser.add_argument('--mode', default='LOOPWAIT', type=str, help='mode')
    parser.add_argument('--disable', default='0', type=int, help='1: disable')
    parser.add_argument('--stl', default='none', type=str, help='stl file')
    parser.add_argument('uut', nargs=1, help="uut")
    run_gpg(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()
