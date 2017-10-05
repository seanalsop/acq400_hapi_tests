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
        u.s0.trace      = args.trace
        u.s1.trace      = args.trace
        u.s0.transient  = 'POST={}'.format(args.post)
        u.s1.trg        = args.trg
        u.s1.RGM        = args.rgm
        u.s1.RGM_DX     = args.dx
        u.s1.RGM_SENSE  = args.sense
        u.s1.RTM_TRANSLEN = args.rtm_translen if args.rgm == 'RTM' else 0
        u.s1.es_enable  = args.es_enable
        dx = args.dx[1:]
        if dx == '1':
            u.s0.set_knob('SIG_SRC_TRG_1', 'GPG1' if args.gpg == 'on' else 'STRIG')
        if dx == '0':
            u.s0.set_knob('SIG_SRC_TRG_0', 'GPG0' if args.gpg == 'on' else 'EXT')
        u.s0.set_arm = 1

    # warning: this is a RACE for the case of a free-running trigger and multiple UUTs
    if args.gpg == 'on':
        raw_input("say when (uuts are armed)")
        for u in uuts:
            u.s0.GPG_ENABLE = '1'
        

def run_main():
    parser = argparse.ArgumentParser(description='set_burst mode')    
    parser.add_argument('--rgm', default='RTM', type=str, help="mode RGM|RTM")
    parser.add_argument('--dx', default='d0', type=str, help='dx d0|d1|d2')
    parser.add_argument('--gpg', default='off', type=str, help='source from gpg on|off')
    parser.add_argument('--sense', default='rising', type=str, help='rising|falling')
    parser.add_argument('--rtm_translen', default=1234, type=int, help='transient length')
    parser.add_argument('--post', default=100000, type=int, help='shot length')
    parser.add_argument('--trg', default='1,0,1', type=str, help='shot trigger triplet')
    parser.add_argument('--es_enable', default=1, type=int, help='0 disables Event Signature')
    parser.add_argument('--trace', default=0, type=int, help='1: enable command trace')
    parser.add_argument('uuts', nargs='+', help="uut")
    configure_bm(parser.parse_args())

# execution starts here

if __name__ == '__main__':
    run_main()
