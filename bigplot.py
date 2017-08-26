#!/usr/bin/python -i

import sys
import acq400_hapi
import awg_data
import argparse
import numpy as np
import matplotlib.pyplot as plt



FMT = "/data/ACQ400DATA/%d/%s/%06d/%d.%02d"
#"/data/ACQ400DATA/%d/acq2106_070/000001/0.02"


def load3(lun=0, uut="acq2106_070", cycle=1, buf0=0, nchan=48):
    if buf0 % 3 != 0:
        print("ERROR, buf %d not modulo 3" % (buf0))
        exit(1)
    b3 = tuple([ np.fromfile(FMT % (lun, uut, cycle, lun, buf0+x), np.int16) for x in range(3)] )
    raw = np.concatenate(b3)
    chx = np.reshape(raw, (raw.size/nchan, nchan))
    return chx



    