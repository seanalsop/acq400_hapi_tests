#!/usr/bin/python -i

import acq400_hapi
import os
import argparse
import sys

parser = argparse.ArgumentParser(description='configure acq400_abort')
parser.add_argument('--sys', default=0, help="run in interpreter loop N times")
parser.add_argument('uut', nargs='+', help="uut")

args = parser.parse_args()
uuts = [ acq400_hapi.Acq400(u) for u in args.uut ]
uut = uuts[0]

def sys1(cmd):
    if cmd.find("=") > 0:
        for u in uuts:
            exec('u.{}'.format(cmd))
    else:
        for u in uuts:
            print("%s" % (eval('u.{}'.format(cmd))))
            
def sys(loop = 1):
    while loop:
        sys1(raw_input(">"))
        loop -= 1
        
if args.sys > 0:
    sys(loop=int(args.sys))

        

    
            

    




