#!/usr/bin/env python
# Hardware In Loop : Hi Gain. Trim AO's until measured loopback is zero 
# upload to AWG and optionally run a capture.
# data for upload is either File (host-local data file) or Rainbow, a test pattern.
# assumes that clocking has been pre-assigned.

import sys
import acq400_hapi
import awg_data
import argparse
import numpy as np
import matplotlib.pyplot as plt

def store_file(it, rdata, nchan, nsam):
    fn = 'DATA/ai%04d.dat' % (it)
    print(("store_file {}".format(fn)))

    with open(fn, 'wb') as f:
        f.write(rdata)

def plot(it, rdata, nchan, nsam):
    chx = np.reshape(rdata, (nsam, nchan))    
    for ch in range(0,nchan):
        plt.plot(chx[:,ch])

    plt.show()
    plt.pause(0.0001)

def run_shots(args):
    uut = acq400_hapi.Acq400(args.uuts[0])
    acq400_hapi.cleanup.init()
    if args.plot:
        plt.ion()

    uut.s0.transient = 'POST=%d SOFT_TRIGGER=%d DEMUX=%d' % \
        (args.post, 1 if args.trg == 'int' else 0, 1 if args.store==0 else 0) 

    for sx in uut.modules:
        uut.modules[sx].trg = '1,1,1'  if args.trg == 'int' else '1,0,1'
    for sx in uut.modules:
        if uut.modules[sx].data32 == '1':
            if uut.modules[sx].adc_18b == '1':
                rshift = 14
            else:
                rshift = 16
        else:
            rshift = 0
        break

    work = awg_data.ZeroOffset(uut, args.nchan, args.awglen, aochan = int(args.aochan), 
                               gain = args.gain, passvalue = args.passvalue, ao0 = args.ao0) 
    store = store_file

    try:
        loader = work.load()
        ii = 0
        while next(loader):        
            uut.run_oneshot()        
            print(("read_chan %d" % (args.post*args.nchan)))
            rdata = uut.read_chan(0, args.post*args.nchan)                        
            if args.plot > 0 :
                plt.cla()
                title = "AI for shot %d %s" % (ii, "persistent plot" if args.plot > 1 else "")
                print(title)
                plt.title(title)
                plot(ii, np.right_shift(rdata, rshift), args.nchan, args.post)
                store(ii, rdata, args.nchan, args.post)
                if args.wait_user:
                    key = input("hit return to continue, q for quit").strip()
                    if key == 'q':
                        work.user_quit = True
                    print(("raw_input {}".format(key)))
                    if uut.s0.data32 == '1':
                        print("scale rdata >> 16")
                        rdata = rdata >> 16
                    work.feedback(np.reshape(rdata, (args.post, args.nchan)))
                    ii += 1
    except StopIteration:
        print("offset zeroed within bounds")
    except acq400_hapi.acq400.Acq400.AwgBusyError:
        print("AwgBusyError, try a soft trigger and quit, then re-run me")
        uut.s0.soft_trigger = '1'



def run_main():
    parser = argparse.ArgumentParser(description='acq1001 HIL zero offset demo')
    parser.add_argument('--gain', type=float, default=0.1, help="set gain constant")
    parser.add_argument('--files', default="", help="list of files to load")
    parser.add_argument('--loop', type=int, default=1, help="loop count")        
    parser.add_argument('--store', type=int, default=1, help="save data when true") 
    parser.add_argument('--nchan', type=int, default=32, help='channel count for pattern')    
    parser.add_argument('--awglen', type=int, default=2048, help='samples in AWG waveform')
    parser.add_argument('--ao0', type=int, default=0, help='first ao in set')
    parser.add_argument('--passvalue', type=int, default=1, help='acceptable error')
    parser.add_argument('--aochan', type=int, default=0, help='AO channel count, if different to AI (it happens)')
    parser.add_argument('--post', type=int, default=100000, help='samples in ADC waveform')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('--plot', type=int, default=1, help='--plot 1 : plot data, 2: persistent')
    parser.add_argument('--wait_user', type=int, default=0, help='1: force user input each shot')
    parser.add_argument('uuts', nargs=1, help="uut ")
    run_shots(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()

