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


# AD9854 class in the making ..
def FTW1(ratio):
	return format(long(ratio * pow(2,48)), '012x')

def set_upd_clk_fpga(uut, idds, value):
    if idds == 0:
	uut.s2.ddsA_upd_clk_fpga = value
    else:
	uut.s2.ddsB_upd_clk_fpga = value
    
	

def init_chirp(uut, idds):
# SETTING KAKA'AKOS CHIRP
#
# Set AD9854 clock remap to 25 MHz
    dds = uut.ddsA if idds == 0 else uut.ddsB

    uut.ddsC.CR     = '004A0041'
    uut.ddsC.FTW1   = FTW1(0.1)

# Program AD9512 secondary clock to choose 25 MHz from the AD9854 remap
    uut.clkdB.CSPD  = '02'
    uut.clkdB.UPDATE = '01'


# Program the chirp using Kaka'ako parameters
    set_upd_clk_fpga(uut, idds, '1')
    dds.CR     = '004F0061'
    dds.FTW1   = '172B020C49BA'
    dds.DFR    = '0000000021D1'
    dds.UCR    = '01F01FD0'
    dds.RRCR   = '000001'
    dds.IPDMR  = '0FFF'
    dds.QPDMR  = '0FFF'
    dds.CR     = '004C8761'
    set_upd_clk_fpga(uut, idds, '0')
    
# Set the trigger
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
	if len(sys.argv) > 2 and sys.argv[2] == "ddsB":
		print "operate on ddsB"
		idds = 1
	else:
		print "operate on ddsA"
		idds = 0
	
        init_chirp(uut, idds)
    else:
        print("USAGE: radcelf-chirp-init UUT1")
        sys.exit(1)        

# execution starts here

if __name__ == '__main__':
    run_main()
