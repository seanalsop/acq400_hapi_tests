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

def csv_name(args, binfile):
    if len(args.out) > 0:
        basename = args.out
    else:
        basename, extn = os.path.splitext(binfile)

    return "{}{}{}.csv".format(args.outroot, os.sep if len(args.outroot)>0 else '', basename)

def bin2csv_onesource_manychan(args):     
    raw = np.fromfile(args.binfiles[0], args.wtype)
    nrows = len(raw)/args.nchan
    chx = np.reshape(raw, (nrows, args.nchan))
        
    with open(args.csvf, 'w' ) as fout:
        writer = csv.writer(fout)
        for row in range(0, nrows):
            writer.writerow(chx[row,:])
                
                
def bin2csv_many_onechan_sources(args):
    chx = list()
    for binf in args.binfiles:
        chx.append(np.fromfile(binf, args.wtype))
    lens = [ len(u) for u in chx ]
    nrows = lens[0]
    chxx = np.vstack(chx)
    
    with open(args.csvf, 'w' ) as fout:
        writer = csv.writer(fout)
        for row in range(0, nrows):
            writer.writerow(chxx[:,row])    
            
def bin2csv(args):
    args.wtype = get_word_type(args.word)
    args.csvf = csv_name( args, args.binfiles[0])
    if len(args.binfiles) == 1:
        bin2csv_onesource_manychan(args)
    else:
        bin2csv_many_onechan_sources(args)
        
def run_main():
    parser = argparse.ArgumentParser(description='bin2csv')
    parser.add_argument('--nchan', default=1, type=int, help="number of channels")
    parser.add_argument('--word', default='int16', help="int16|int32")
    parser.add_argument('--outroot', default='', help="output root directory")
    parser.add_argument('--out', default='', help="explicit output name")
    parser.add_argument('binfiles', nargs='+', help="file to convert either a single file * nchan or paste multiple files * 1 chan")
    bin2csv(parser.parse_args())
     
    
    
# execution starts here

if __name__ == '__main__':
    run_main()
