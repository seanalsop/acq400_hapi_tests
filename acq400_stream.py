#!/usr/bin/env python

"""
This is a script intended to connect to a UUT and
stream data from port 4210.
"""

import acq400_hapi
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import argparse


# make_data_dir creates a subdirectory
# where data is to be stored.
def make_data_dir(direc):
    try:
        os.mkdir(direc)
    except Exception:
        pass


def run_stream(args):
    num = 0
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts]

    for uut in uuts:
        channum = uut.s0.NCHAN
        print(int(channum))
        try:
            if uut.s0.data32:
                wordsizetype = "<i4"  # 32 bit little endian
                wordsize = 32
        except AttributeError:
            print("Attribute error detected. No data32 attribute - defaulting to 16 bit")
            wordsizetype = "<i2"  # 16 bit little endian
            wordsize = 16

        skt = acq400_hapi.Netclient(args.uuts[0], 4210)  # Needs to be string
        start_time = time.clock()
        make_data_dir(args.root)

        while time.clock() < (start_time + args.runtime):

            data = skt.sock.recv(args.filesamples*wordsize*(int(channum)))
            data_file = open("{}/data{}.dat".format(args.root, num), "wb")
            data = np.frombuffer(data, dtype=wordsizetype, count=-1)

            if args.plot == 1:
                plt.plot(data[::32])
                plt.show()

            data.tofile(data_file, '')
            num += 1
            data_file.close()


def run_main():
    parser = argparse.ArgumentParser(description='acq400 stream')
    parser.add_argument('--filesamples', default=10, type=int, help="Number of samples to store in file")
    parser.add_argument('--root', default="ROOT", type=str, help="Location to save files")
    parser.add_argument('--runtime', default=5, type=int, help="How long to stream data for")
    parser.add_argument('--plot', default=0, type=int, help='Whether the data streamed from the loop is plotted - pauses stream')
    parser.add_argument('--verbose', default=1, type=int, help='Prints status messages as the stream is running')
    parser.add_argument('uuts', nargs='+', help="uuts")

    run_stream(parser.parse_args())


if __name__ == '__main__':
    run_main()
