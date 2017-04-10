#!/usr/bin/env python

import acq400_hapi
import os

uuts = [ acq400_hapi.Acq400(u) for u in os.getenv("UUTS").split(" ")]

for u in uuts:
	u.s0.TIM_CTRL_LOCK = 0
	u.s0.set_abort = 1


