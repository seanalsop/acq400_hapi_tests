#!/usr/bin/env python
# mgtdramsshot.py
# assumes that clocking has been pre-assigned.

import sys
import datetime
import acq400_hapi
import awg_data
import argparse
from subprocess import call
import re

import os

LOG = None

def write_console(message):
# explicit flush needed to avoice lockup on Windows.    
    sys.stdout.write(message)
    sys.stdout.flush()


class UploadFilter:
    def __init__(self):
        self.okregex = re.compile(r"axi0 start OK ([0-9]{4}) OK")
        self.line = 0

    def __call__ (self, st):
        st = st.rstrip()
        LOG.write("{}\n".format(st))

        if self.okregex.search(st) != None:
            if self.line%10 != 0:
                write_console('.')
            else:
                write_console("{}".format(self.line/10))
            self.line += 1
            if self.line > 100:
                write_console('\n')
                self.line = 0
        else:
            if self.line != 0:
                write_console('\n')
            write_console(">{}\n".format(st))
            self.line = 0


def set_simulate(uut, enable):
    for s in uut.modules:
        uut.modules[s].simulate = '1' if enable else '0'

def run_shot(uut, args):
        # always capture over. The offload is zero based anyway, so add another one
    if args.captureblocks:
        uut.s14.mgt_run_shot = str(int(args.captureblocks) + 2)
        uut.run_mgt()

    uut.s14.mgt_offload = args.offloadblocks if args.offloadblocks != 'capture' \
        else '0-{}'.format(args.captureblocks)
    t1 = datetime.datetime.now()
    uut.run_mgt(UploadFilter())
    ttime = datetime.datetime.now()-t1
    mb = args.captureblocks*4
    print("upload {} MB done in {} seconds, {} MB/s\n".\
          format(mb, ttime, mb/ttime.seconds))
    if args.validate != 'no':
        cmd = "{} {}".format(args.validate, uut.uut)
        print "run \"{}\"".format(cmd)
        rc = call(cmd, shell=True, stdin=0, stdout=1, stderr=2)
        if rc != 0:
            print("ERROR called process {} returned {}".format(args.validate, rc))
            exit(1)

def run_shots(args):
    global LOG
    LOG = open("mgtdramshot-{}.log".format(args.uut[0]), "w")
    uut = acq400_hapi.Acq2106(args.uut[0], has_mgtdram=True)
    uut.s14.mgt_taskset = '1'
    set_simulate(uut, args.simulate)

    try:
        for ii in range(0, args.loop):
            t1 = datetime.datetime.now()
            print("shot: {} {}".format(ii, t1.strftime("%Y%m%d %H:%M:%S")))
            run_shot(uut, args)
            t2 = datetime.datetime.now()
            print("done in {} seconds\n\n".format((t2-t1).seconds))

            if args.wait_user:
                raw_input("hit return to continue")
    except KeyboardInterrupt:
        print("Keyboard Interrupt, take it all down NOW")
        os._exit(1)

    os.exit(0)

def run_main():
    parser = argparse.ArgumentParser(description='acq2106 mgtdram test')
    parser.add_argument('--loop', type=int, default=1, help="loop count")
    parser.add_argument('--captureblocks', type=int, default="2000", help='number of 4MB blocks to capture')
    parser.add_argument('--offloadblocks', type=str, default="capture", help='block list to upload nnn-nnn')
    parser.add_argument('--validate', type=str, default='no', help='program to validate data')
    parser.add_argument('--trg', default="int", help='trg "int|ext rising|falling"')
    parser.add_argument('--wait_user', type=int, default=0, help='1: force user input each shot')
    parser.add_argument('--simulate', type=int, default=1, help='enable simulate (ramp) on modules')
    parser.add_argument('uut', nargs=1, help="uut ")
    run_shots(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()
