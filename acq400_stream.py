#!/usr/bin/env python

"""
This is a script intended to connect to a UUT and
stream data from port 4210.

The data that has been streamed is not demuxed and
so if it is to be used then it has to be demuxed first.
Something like:

data = numpy.fromfile("data0.dat", dtype="<datatype>")
plt.plot(data[::<number of channels>])
plt.show()

Notes:
If filesize > total data then no data will be stored.
If runtime is too short then no data will be stored.

The default runtime is large so that the user can
specify total data required rather than time to run.
If a runtime is more applicable then specify a large
total data and the run time required.
"""

import acq400_hapi
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import argparse


# make_data_dir creates a subdirectory
# where data is to be stored.
def make_data_dir(directory, verbose):
    try:
        os.mkdir(directory)
    except Exception:
        if verbose:
            print "Exception met while creating data directory: Passing"
        pass


def run_stream(args):

    data = ""
    num = 0
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts]

    for uut in uuts:
        channum = uut.s0.NCHAN
        # print(int(channum))
        try:
            if uut.s0.data32:
                wordsizetype = "<i4"  # 32 bit little endian
                wordsize = 32
        except AttributeError:
            print("Attribute error detected. No data32 attribute - defaulting to 16 bit")
            wordsizetype = "<i2"  # 16 bit little endian
            wordsize = 16

        skt = acq400_hapi.Netclient(args.uuts[0], 4210)  # Needs to be string
        make_data_dir(args.root, args.verbose)
        start_time = time.clock()
        upload_time = time.clock()
        data_length = 0

        while time.clock() < (start_time + args.runtime) and data_length < args.totaldata:

            loop_time = time.clock()
            data += skt.sock.recv(1024)

            if len(data) / 1024 >= args.filesize:

                data_file = open("{}/data{}.dat".format(args.root, num), "wb")
                data = np.frombuffer(data, dtype=wordsizetype, count=-1)

                if args.plot == 1:
                    plt.plot(data[::32])
                    plt.show()

                data.tofile(data_file, '')
                data_length += float(len(data)) / 1024

                if args.verbose == 1:
                    print "New data file written."
                    print "Data Transferred: ", data_length, "KB"
                    print "loop_time: ", loop_time
                    print "Data upload & save rate: ", float(len(data))/1024/((time.clock()-upload_time)), "KB/s"

                num += 1
                data_file.close()

                data = "" # Remove data from variable once it has been written
                upload_time = time.clock() # Reset upload time



def run_main():
    parser = argparse.ArgumentParser(description='acq400 stream')
    parser.add_argument('--filesize', default=2048, type=int, help="Size of file to store in KB. If filesize > total data then no data will be stored.")
    parser.add_argument('--totaldata', default=4096, type=int, help="Total amount of data to store in KB")
    parser.add_argument('--root', default="ROOT", type=str, help="Location to save files")
    parser.add_argument('--runtime', default=1000, type=int, help="How long to stream data for")
    parser.add_argument('--plot', default=0, type=int, help='Whether the data streamed from the loop is plotted - pauses stream')
    parser.add_argument('--verbose', default=0, type=int, help='Prints status messages as the stream is running')
    parser.add_argument('uuts', nargs='+', help="uuts")

    run_stream(parser.parse_args())


if __name__ == '__main__':
    run_main()
