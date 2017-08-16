
import numpy as np

class RunsFiles:
    def __init__(self, uut, files, run_forever=False):
        self.uut = uut
        self.files = files
        self.run_forever = run_forever
        
    def load(self):
        for ii in range(99999 if self.run_forever else 1):
            for f in self.files:
                with open(f, mode='r') as fp:
                    self.uut.load_awg(fp.read())
                yield f 
            
    
class SinGen:
    NCYCLES = 5
    def sin(self):
        nsam = self.nsam
        NCYCLES = self.NCYCLES
        return np.sin(np.array(range(nsam))*NCYCLES*2*np.pi/nsam)   # sin, amplitude of 1 (volt)

class AllFullScale(SinGen):
    def __init__(self, uut, nchan, nsam, run_forever=False):
        self.uut = uut
        self.nchan = nchan
        self.nsam = nsam
        self.run_forever = run_forever
        self.sw = self.sin()
        self.aw = np.zeros((nsam,nchan))
        for ch in range(nchan):
            self.aw[:,ch] = self.sw

    def load(self):
        for ii in range(99999 if self.run_forever else 1):
            for ch in range(self.nchan):
                self.uut.load_awg((self.aw*(2**15-1)).astype(np.int16))
                print("loaded array ", self.aw.shape)
                yield ch
    


class RainbowGen:
    NCYCLES = 5
    def offset(self, ch):
        return -9.0 + 8.0*ch/self.nchan;
    
    def rainbow(self, ch):
        return np.add(self.sw, self.offset(ch))
    
    def sin(self):
        nsam = self.nsam
        NCYCLES = self.NCYCLES    
        return np.sin(np.array(range(nsam))*NCYCLES*2*np.pi/nsam)   # sin, amplitude of 1 (volt)
        
    def sinc(self, ch):
        nsam = self.nsam
        nchan = self.nchan
        NCYCLES = self.NCYCLES
        xoff = ch*100
        xx = np.array(range(-nsam/2-xoff,nsam/2-xoff))*NCYCLES*2*np.pi/nsam
        return [ np.sin(x)/x if x != 0 else 1 for x in xx ]
    
    def __init__(self, uut, nchan, nsam, run_forever=False):
        self.uut = uut
        self.nchan = nchan
        self.nsam = nsam
        self.run_forever = run_forever
        self.sw = self.sin()        
        self.aw = np.zeros((nsam,nchan))
        for ch in range(nchan):
            self.aw[:,ch] = self.rainbow(ch)            
#            self.aw[:,ch] = self.rainbow(1)

    def load(self):
        for ii in range(99999 if self.run_forever else 1):
            for ch in range(self.nchan):        
                aw1 = np.copy(self.aw)
                aw1[:,ch] = np.add(np.multiply(self.sinc(ch),5),2)
                print("loading array ", aw1.shape)
                self.uut.load_awg((aw1*(2**15-1)/10).astype(np.int16))           
                print("loaded array ", aw1.shape)
                yield ch
