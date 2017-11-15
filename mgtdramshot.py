#!/usr/bin/env python
# mgtdramsshot.py
# assumes that clocking has been pre-assigned.

import sys
import acq400_hapi
import awg_data
import argparse
from subprocess import call
import re


LOG = open("mgtdramshot.log", "w")

class UploadFilter:
    def __init__(self):
        self.okregex = re.compile(r"axi0 start OK ([0-9]{4}) OK")
        self.line = 0
        
    def __call__ (self, st):
        LOG.write(st)
        
        if self.okregex.search(st) != None:
            sys.stdout.write('.')
            sys.stdout.flush()
            self.line += 1
            if self.line > 100:
                sys.stdout.write('\n')
                self.line = 0
        else:
            if self.line != 0:
                sys.stdout.write('\n')
            print(">{}".format(st))
            self.line = 0            
   
    

def run_shot(uut, args):
    uut.s14.mgt_run_shot = args.captureblocks
    uut.run_mgt()
    uut.s14.mgt_offload = args.offloadblocks if args.offloadblocks != 'capture' \
        else '0-{}'.format(args.captureblocks)
    uut.run_mgt(UploadFilter())
    if args.validate != 'no':
        rc = call("{} {}".format(args.validate, uut), shell=True, stdin=0, stdout=1, stderr=2)
        if rc != 0:
            print("ERROR called process {} returned {}".format(args.validate, rc))
            exit(1)
    
def run_shots(args):
    uut = acq400_hapi.Acq2106(args.uut[0], has_mgtdram=True)
    uut.s14.mgt_taskset = '1'
    
    for ii in range(0, args.loop):
        print("shot: %d" % (ii))
        run_shot(uut, args)
        
        if args.wait_user:
            raw_input("hit return to continue")


def run_main():
    parser = argparse.ArgumentParser(description='acq2106 mgtdram test')    
    parser.add_argument('--loop', type=int, default=1, help="loop count")     
    parser.add_argument('--captureblocks', type=str, default="2000", help='number of 4MB blocks to capture')
    parser.add_argument('--offloadblocks', type=str, default="capture", help='block list to upload nnn-nnn')
    parser.add_argument('--validate', type=str, default='no', help='program to validate data')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('--wait_user', type=int, default=0, help='1: force user input each shot')
    parser.add_argument('uut', nargs=1, help="uut ")
    run_shots(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()