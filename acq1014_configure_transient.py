#!/usr/bin/env python

""" configure transient 
    acq1014_configure_transient UUT1 UUT2 [NPOST] [trigger=int|ext|ext2]
"""

import sys
import acq400_hapi
import argparse
import sets



def configure_shot(args):
    if len(args.uuts)%2:
        print("ERROR: must be an even number of uuts, minimum 2")
        sys.exit(1)
        
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts]    
    mset = sets.Set(uuts[0:2])
    
    for u in reversed(uuts):
        print("uut:%s" % u.uut)
        u.s0.trace = 1;
        
        t_args = args.trg.split(' ')
        if len(t_args) > 1:
            t_args[1] = "prepost" if args.pre>0 else "post"
        u.s0.acq1014_select_trg_src = ' '.join(t_args)
        
        if u in mset:
            u.s0.acq1014_select_clk_src = args.clk
        else:
            optargs = args.clk.split(' ')[1:]
            u.s0.acq1014_select_clk_src = 'int ' + ' '.join(optargs)
            
        u.s0.trace = 0

def run_main():
    parser = argparse.ArgumentParser(description='configure multiple acq1014')
    parser.add_argument('--pre', type=int, default=0, help="pre trigger length")
    parser.add_argument('--post', type=int, default=100000, help="post trigger length")
    parser.add_argument('--clk', default="int 50000000", help='clk "int|ext SR [CR]"')
    parser.add_argument('--trg', default="int", help='trg "int|ext post rising|falling"')
    parser.add_argument('uuts', nargs='*', help="uut pairs: m1,m2 [s1,s2 ...]")
    configure_shot(parser.parse_args())


# execution starts here

if __name__ == '__main__':
    run_main()

