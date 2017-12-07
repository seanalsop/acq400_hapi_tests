#!/usr/bin/env python

""" bin2csv
    input raw binary, output csv
"""

import csv
import argparse
import numpy as np
import os

def get_word_type(wtype):
    if wtype == 'int16':
        return np.int16
    elif wtype == 'int32':
        return np.int32
    else:
        print("ERROR, undefined word type {}".format(wtype))
        exit(1)

def bin2csv(args):
    wtype = get_word_type(args.word)
    for binf in args.binfiles:
        raw = np.fromfile(binf, wtype)
        nrows = len(raw)/args.nchan
        chx = np.reshape(raw, (nrows, args.nchan))
        csvf, extn = os.path.splitext(binf)
        
        with open("{}./{}.csv".format(args.outroot, csvf), 'w' ) as fout:
            writer = csv.writer(fout)
            for row in range(0, nrows):
                writer.writerow(chx[row,:])

def run_main():
    parser = argparse.ArgumentParser(description='bin2csv')
    parser.add_argument('--nchan', default=1, type=int, help="number of channels")
    parser.add_argument('--word', default='int16', help="int16|int32")
    parser.add_argument('--outroot', default='', help="output root directory")
    parser.add_argument('binfiles', nargs='+', help="files to convert")
    bin2csv(parser.parse_args())
    
# execution starts here

if __name__ == '__main__':
    run_main()
