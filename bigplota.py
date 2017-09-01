#!/usr/bin/python -i

import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import subprocess


FMT = "%s/ACQ400DATA/%d/%s/%06d/%d.%02d"
#"/data/ACQ400DATA/%d/acq2106_070/000001/0.02"

def get_uut():
    p1 = subprocess.Popen(['get-ident'], stdout=subprocess.PIPE)
    return p1.communicate()[0].strip().split(' ')
    

uut = "acq2106_000"
(host, uut) = get_uut()

def load3(base="/data", lun=0, uut=uut, cycle=1, buf0=0, nchan=48):
    if buf0 % 3 != 0:
        print("ERROR, buf %d not modulo 3" % (buf0))
        exit(1)
    print("load3 {}".format(FMT % (base, lun, uut, cycle, lun, buf0)))
    b3 = tuple([ np.fromfile(FMT % (base, lun, uut, cycle, lun, buf0+x), np.int16) for x in range(3)] )
    raw = np.concatenate(b3)
    chx = np.reshape(raw, (raw.size/nchan, nchan))
    return (chx, lun, uut, cycle, nchan)

def plot16(l3, ic=0, nc=16):
    (chx, lun, uut, cycle, nchan) = l3
    for ch in range(ic,ic+nc):
        plt.plot(chx[:,ch])
        
    plt.title("uut: {} lun:{} ch {}..{}".format(uut, lun, ic+1, ic+nc+1))
    plt.xlabel("cycle {:06}".format(cycle))
    plt.show()
    

class LoadsHost:
        def __init__(self, host, uut):
            self.uut = uut
            self.host = host
            
        def load3(self, lun=0, cycle=1, buf0=0, nchan=48):
            return load3("data/{}".format(self.host), lun, self.uut, cycle, buf0, nchan)
       
loaders = [ LoadsHost(h, u) for (h, u) in (("Bolby", "acq2106_070"), ("Betso", "acq2106_071"),
                                       ("Ladna", "acq2106_072"), ("Vindo", "acq2106_073"))]
        
def get4(lun=0, cycle=1, buf0=0):
    return [ l.load3(lun, cycle, buf0) for l in loaders]

lenb = 0x400000
len3 = 3*lenb
ssize= 48*2
sam3 = len3/ssize
buffc = 99
buffc3 = buffc/3

M1 = 1000000
SR = 2*M1

pulsem = (0, 2, 4, 10, 20, 40, 100, 200)
pp = 0
for p in pulsem:
    samples = p*M1    
    buf3s = samples / sam3    
    residue = samples - buf3s * sam3            # residue, samples in triplet
    cycle = buf3s/buffc3                        # cycle from 0   
    cycb = 3*(buf3s - cycle*buffc3)              # buffer in cycle, first of 3
    
    buffers = buf3s * 3     
    cycle += 1                                  # counts from 1
    
    print("samples {} buffers {} residue {} cycle {} buffc {}".format(
        samples, buffers, residue, cycle, cycb))
    chx = get4(cycle=cycle, buf0=cycb)
    for m in range(0,4):
	for c in range(0,1):
	    plt.plot(chx[m][0][:,c], label='a{}.{}'.format(chx[m][2][8:], c))
        
    plt.legend(loc='upper left', bbox_to_anchor=(1,1))
    plt.title("UUTS {} at t {}s, pulse {} at sample {}".format("ALL", p*M1/SR, pp, p*M1))   
    plt.axvline(x=residue)
    plt.xlabel('cycle:{} buf:{}'.format(cycle, cycb))
    plt.show()          
    pp += 1




    
