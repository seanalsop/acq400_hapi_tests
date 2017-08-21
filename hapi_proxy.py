#!/usr/bin/python -i

import acq400_hapi
import os
import argparse
import sys

parser = argparse.ArgumentParser(description='configure acq400_abort')
parser.add_argument('uut', nargs='+', help="uut")

args = parser.parse_args()
uuts = [ acq400_hapi.Acq400(u) for u in args.uut ]
uut = uuts[0]

def sys():
    cmd = raw_input(">")
    if cmd.find("=") > 0:
        for u in uuts:
            exec('u.{}'.format(cmd))
    else:
        for u in uuts:
            print("%s" % (eval('u.{}'.format(cmd))))
            

    




