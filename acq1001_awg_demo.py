#!/usr/bin/env python

import sys
import acq400_hapi
import numpy as np
import matplotlib.pyplot as plt
import argparse
import timeit

class RunsFiles:
    def __init__(self, uut, files):
        self.uut = uut
        self.files = files
        
    def load(self):
        for f in self.files:
            with open(f, mode='r') as fp:
                self.uut.load_awg(fp.read())
            yield f        


class RainbowGen:
    NCYCLES = 5
    def offset(self, ch):
        return -9.0 + 8.0*ch/self.nchan;
    
    def rainbow(self, ch):
        return np.add(self.sw, self.offset(ch))
    
    def sin(self):
        nsam = self.nsam
        NCYCLES = self.NCYCLES    
        return np.sin(np.array(range(nsam))*NCYCLES*2*np.pi/nsam)   # sin, amplitude of 1 (volt)
        
    def sinc(self, ch):
        nsam = self.nsam
        nchan = self.nchan
        NCYCLES = self.NCYCLES
        xoff = ch*nsam/NCYCLES/10
        xx = np.array(range(-nsam/2-xoff,nsam/2-xoff))*NCYCLES*2*np.pi/nsam
        return [ np.sin(x)/x if x != 0 else 1 for x in xx ]
    
    def __init__(self, uut, nchan, nsam):
        self.uut = uut
        self.nchan = nchan
        self.nsam = nsam        
        self.sw = self.sin()        
        self.aw = np.zeros((nsam,nchan))
        for ch in range(nchan):
            self.aw[:,ch] = self.rainbow(ch)

    
    def load(self):        
        #for ch in range(self.nchan):
        for ch in range(8):             # convenient to plot 8
            aw1 = np.copy(self.aw)
            aw1[:,ch] = np.add(np.multiply(self.sinc(ch),5),2)
            print("loading array ", aw1.shape)
            self.uut.load_awg((aw1*(2**15-1)/10).astype(np.int16))           
            print("loaded array ", aw1.shape)
            yield ch
        
def run_shots(args):
    uut = acq400_hapi.Acq400(args.uuts[0])
    acq400_hapi.cleanup.init()
    if args.capture > 0:
        uut.s0.transient = 'POST=%d SOFT_TRIGGER=%d' % \
            (args.post, 1 if args.trg == 'int' else 0)
        shot_controller = acq400_hapi.ShotController([uut])
    
    for sx in uut.modules:
        uut.modules[sx].trg = '1,1,1'  if args.trg == 'int' else '1,0,1'
    
    if args.files != "":
        work = RunsFiles(uut, args.files.split(','))
    else:
        work = RainbowGen(uut, args.nchan, args.awglen)
        
    for ii in range(0, args.loop):
        print("shot: %d" % (ii))
            
        for f in work.load():
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
    parser.add_argument('--awglen', type=int, default=2048, help='samples in AWG waveform')
    parser.add_argument('--post', type=int, default=100000, help='samples in ADC waveform')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('uuts', nargs=1, help="uut ")
    run_shots(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()



