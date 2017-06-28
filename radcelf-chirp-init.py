#!/usr/bin/env python

""" radcelf-chirp-init - set up a chirp ..
    radcelf-chirp-init UUT1
    where UUT1 is the ip-address or host name of the uut
    powerful alternative to embedded shell script.
    
    no ssh keys or remote execution, nfs mounts required.
    
    potential enhancements stepping stone to avoid the magic numbers:
    eg
            AD9854.CR.X4 = 00040000
    potential to program real numbers eg
      >>> format(long(0.5 * pow(2,48)), '012x')
     '800000000000'
  
    seamless integration with data capture (and maybe postprocess and analysis..)
"""

import sys
import acq400_hapi


def init_chirp(uut):
# SETTING KAKA'AKOS CHIRP
#
# Set AD9854 clock remap to 25 MHz
    uut.ddsC.CR     = '004C0041'
    uut.ddsC.FTW1   = '1AAAAAAAAAAA'

# Program AD9512 secondary clock to choose 25 MHz from the AD9854 remap
    uut.clkdB.CSPD  = '02'
    uut.clkdB.UPDATE = '01'


# Program the chirp using Kaka'ako parameters
    uut.s2.ddsA_upd_clk_fpga = '1'
    uut.ddsA.CR     = '004F0061'
    uut.ddsA.FTW1   = '172B020C49BA'
    uut.ddsA.DFR    = '0000000021D1'
    uut.ddsA.UCR    = '01F01FD0'
    uut.ddsA.RRCR   = '000001'
    uut.ddsA.IPDMR  = '0FFF'
    uut.ddsA.QPDMR  = '0FFF'
    uut.ddsA.CR     = '004C8761'

# Set the trigger
    uut.s2.ddsA_upd_clk_fpga = 0
    
# lera_acq_setup
# we assume a 25MHz from ddsC
# trigger from site 3 ddsA
    uut.s1.trg  = '1,3,1'
    uut.s1.clk  = '1,3,1'
    uut.s1.hi_res_mode = '1'
# 25 MHz/4 = 6.25MHz / 512 = SR 12207
    uut.s1.CLKDIV   = '4'
    

def run_main():           
    if len(sys.argv) > 1:       
        uut = acq400_hapi.RAD3DDS(sys.argv[1])
        init_chirp(uut)
    else:
        print("USAGE: radcelf-chirp-init UUT1")
        sys.exit(1)        

# execution starts here

if __name__ == '__main__':
    run_main()