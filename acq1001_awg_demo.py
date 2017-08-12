#!/usr/bin/env python

import sys
import acq400_hapi
import numpy as np
import matplotlib.pyplot as plt
import argparse

class RunsFiles:
    def __init__(self, uut, files):
        self.uut = uut
        self.files = files
        
    def generate(self):
        for f in self.files:
            with open(f, mode='r') as fp:
                self.uut.load_awg(fp.read())
            yield f        
        
def run_shots(args):
    uut = acq400_hapi.Acq400(args.uuts[0])
    acq400_hapi.cleanup.init()
    shot_controller = acq400_hapi.ShotController([uut])
    
    if args.files != "":
        work = RunsFiles(uut, args.files.split(','))
        
    for ii in range(0, args.loop):
        print("shot: %d" % (ii))
            
        for f in work.generate():
            print("Loaded %s" % (f))
            if args.capture > 0:
                shot_controller.run_shot(soft_trigger= True if args.trg=='int' else False)
            else:
                raw_input("hit return when done")
            

def run_main():
    parser = argparse.ArgumentParser(description='acq1001 awg demo')
    parser.add_argument('--files', default="", help="list of files to load")
    parser.add_argument('--loop', type=int, default=1, help="loop count")
    parser.add_argument('--capture', type=int, default=0, help="run a capture (assumes ADC present)")    
    parser.add_argument('--nchan', type=int, default=32, help='channel count for pattern')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('uuts', nargs=1, help="uut ")
    run_shots(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()



