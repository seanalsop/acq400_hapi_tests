#!/usr/bin/env python

""" configure transient 
    acq1014_configure_transient UUT1 UUT2 [NPOST] [trigger=int|ext|ext2]
"""

import sys
import acq400_hapi
from acq400_hapi import intSI as intSI
import argparse
import sets


def configure_shot(args):        
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts]  
    for uut in uuts:
        if hasattr(uut.s0, 'TIM_CTRL_LOCK'):
            print "LOCKDOWN {}".format(uut)
            uut.s0.TIM_CTRL_LOCK = 0
            
    mset = sets.Set(uuts[0:2])
    pre = intSI(args.pre)
    post = intSI(args.post)
    t_args = [args.trg.split(' ')[0], 
                  "prepost" if pre>0 else "post", 
                  "falling" if "falling" in args.trg else "rising"]    
    c_args = args.clk.split(' ')
    if len(c_args) > 1:
        c_args[1] = intSI(c_args[1])
        if len(c_args) > 2:
            c_args[2] = intSI(c_args[2])
    c_args = [str(x) for x in c_args]

    
    for u in uuts:
        print("uut:%s" % u.uut)
        for svn, svc in sorted(u.svc.items()):
            svc.trace = 1
        
        u.s0.transient = "PRE=%d POST=%d SOFT_TRIGGER=%d" % (pre, post, 1 if pre>0 else 0)
        if pre != 0:
            u.s1.trg="1,1,1"
            u.s1.event0="1,0,1"
        else:
            u.s1.trg="1,0,1"
            u.s1.event0="0,0,0"
        #if u == uuts[0]:
            #u.s1.trg="1,1,1"      # local d1 trg
        #else:
            #u.s1.trg="1,0,1"      # HDMI trg d0 only
        #u.s2.simulate = 1           
        


def run_main():
    parser = argparse.ArgumentParser(description='configure multiple acq1014')
    parser.add_argument('--pre', default=0, help="pre trigger length")
    parser.add_argument('--post', default=100000, help="post trigger length")
    parser.add_argument('--clk', default="int 50000000", help='clk "int|ext SR [CR]"')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('uuts', nargs='+', help="uut pairs: m1,m2 [s1,s2 ...]")
    configure_shot(parser.parse_args())


# execution starts here

if __name__ == '__main__':
    run_main()

