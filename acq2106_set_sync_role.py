#!/usr/bin/env python

""" 
acq2106_set_sync_role master [slave1 ... slaveN]
"""

import argparse
import acq400_hapi

def set_mb_clk(uut, clkdef):
    if (len(clkdef) == 3):
        (src, hz, fin) = clkdef
        uut.set_mb_clk(hz=hz, src=src, fin=fin)
    else:
        (src, hz) = clkdef
        uut.set_mb_clk(hz=hz, src=src)
    
    
def rf(edge):
    return 1 if edge == "rising" else 0

def run_main(parser):
    uuts = [ acq400_hapi.Acq2106(addr) for addr in parser.uuts ]      
    role = "master"
    
    for uut in uuts:
        uut.s0.trace = 1
        if role == "master":
            trg = "1,%d,%d" % (1 if parser.master_trg=="int" else 0, rf(parser.trg_edge))
            
            uut.set_sync_routing_master()
            # ensure there are two values to unpack, provide a default for the 2nd value..
            mtrg, edge = (parser.master_trg.split(',') + [ "rising" ])[:2]            
            uut.set_master_trg(mtrg, edge, \
                               enabled = True if parser.master_trg=="int" else False)
            set_mb_clk(uut, parser.master_clk.split(','))            
            role = "slave"
        else:
            trg = "1,%d,%d" % (0, rf(parser.trg_edge))
            uut.set_sync_routing_slave()
            
        uut.s0.SIG_TRG_EXT_RESET = '1'  # self-clears   
        
        uut.s1.trg = trg
        uut.s1.clk = '1,0,1'
        uut.s1.clkdiv = parser.clkdiv
     
    if parser.master_trg != "int":
         raw_input("say when")
         uuts[0].set_master_trg(mtrg, edge, enabled=True)       
        

# execution starts here

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="acq2106_set_sync_role")
    parser.add_argument("--master_clk", default="zclk,2000000", help="master_clk role alt fp,sysclk,sampleclk")
    parser.add_argument("--master_trg", default="int", help="master_trg src alt fp")
    parser.add_argument("--trg_edge", default="rising", help="selects trigger edge all modules")
    parser.add_argument("--clkdiv", default="1", help="clock divider, each module")
    parser.add_argument("uuts", nargs='+', help="uut pairs: m1 [s1 s2 ...]")
    run_main(parser.parse_args())


