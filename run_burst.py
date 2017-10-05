#!/usr/bin/env python

""" set burst mode
    run_gpg.py [opts] uut
"""

import sys
import acq400_hapi
import argparse
import re


def configure_bm(args):
    uuts = [acq400_hapi.Acq400(u) for u in args.uuts]

    for u in uuts:
        u.s1.RGM        = args.rgm
        u.s1.RGM_DX     = args.dx
        u.s1.RGM_SENSE  = args.sense
        if args.rgm == 'RTM':
            u.s1.RTM_TRANSLEN = args.rtm_translen
        u.s1.es_enable  = args.es_enable
        

def run_main():
    parser = argparse.ArgumentParser(description='run_gpg')    
    parser.add_argument('--rgm', default='RTM', type=str, help="mode RGM|RTM")
    parser.add_argument('--dx', default='d0', type=str, help='dx d0|d1|d2')
    parser.add_argument('--sense', default='rising', type=str, help='rising|falling')
    parser.add_argument('--rtm_translen', default=1234, type=int, help='transient length')
    parser.add_argument('--es_enable', default='1', type=int, help='0 disables Event Signature')
    parser.add_argument('uuts', nargs='+', help="uut")
    configure_bm(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()
