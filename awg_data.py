
import numpy as np
import os


class AwgDefaults:
    def __init__(self, uut_name):
        self.defs = "DATA/{}.npy".format(uut_name)

    def read_defaults(self):        
        print("read_defaults {}".format(self.defs))
        with open(self.defs, 'r') as fp:
            current = np.load(fp)
        print("read_defaults {} {}".format(self.defs, current))
        return current

    def store_defaults(self, current):
        print("store_defaults {} {}".format(self.defs, current))
        with open(self.defs, 'w') as fp:
            np.save(fp, current)


class RunsFiles:
    def __init__(self, uut, files, run_forever=False):
        self.uut = uut
        self.files = files
        self.run_forever = run_forever

    def load(self, autorearm = False):
        for ii in range(99999 if self.run_forever else 1):
            for f in self.files:
                with open(f, mode='rb') as fp:
                    self.uut.load_awg(fp.read(), autorearm = autorearm)
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

    def load(self, autorearm = False):
        for ii in range(99999 if self.run_forever else 1):
            for ch in range(self.nchan):
                self.uut.load_awg((self.aw*(2**15-1)).astype(np.int16), autorearm = autorearm)
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

    def __init__(self, uut, nchan, nsam, run_forever=False, ao0 = 0):
        self.uut = uut
        self.nchan = nchan
        self.nsam = nsam
        self.ao0 = ao0
        self.run_forever = run_forever
        self.sw = self.sin()        
        self.aw = np.zeros((nsam,nchan))
        self.defs = AwgDefaults(uut.uut)
        self.gain = 1.0
        try:   
            self.current = self.defs.read_defaults()
            print("self.current len {} self.nchan {}".format(len(self.current), self.nchan))
            for ch in range(0, len(self.current)):            
                self.aw[:,self.ao0+ch] = self.current[ch]    
        except IOError:
            self.current = np.zeros(self.nchan)
            print("no defaults")

        for ch in range(nchan):
            self.aw[:,ch] = self.rainbow(ch)            

    def load(self, autorearm = False):
        for ii in range(99999 if self.run_forever else 1):
            for ch in range(self.nchan):        
                aw1 = np.copy(self.aw)
                aw1[:,ch] = np.add(np.multiply(self.sinc(ch),5),2)
                print("loading array ", aw1.shape)
                awr = (aw1*(2**15-1)/10)/self.gain
                for chx in range(len(self.current)):
                    awr[:,self.ao0+chx] += self.current[chx]
                self.uut.load_awg(awr.astype(np.int16), autorearm = autorearm)
                print("loaded array ", aw1.shape)
                yield ch

class Pulse:
    def generate(self):
        zset = np.zeros(self.interval)
        pset = zset
        pset[self.interval-1-self.flat_top:] = 1

        for seg in range(1, self.nsam/self.interval):
            x1 = seg*self.interval
            x2 = x1 + self.interval
            for ch in range(self.nchan):
                if seg%self.nchan == ch:
                    self.aw[x1:x2,ch] = pset


    def __init__(self, uut, nchan, nsam, args = (1000,10)):
        self.uut = uut
        self.nchan = nchan
        self.nsam = nsam
        (self.interval, self.flat_top) = [ int(u) for u in args ]
        print( "self.interval {}".format(self.interval)) 
        self.aw = np.zeros((nsam,nchan))
        self.generate()
    def load(self, autorearm = False):
        self.uut.load_awg((self.aw*(2**15-1)/10).astype(np.int16), autorearm = autorearm)
        yield self




class ZeroOffset:   
    def __init__(self, uut, nchan, nsam, run_forever=False, gain = 0.1, passvalue = 1, aochan = 0, ao0 = 0):
        print("ZeroOffset")
        self.uut = uut
        self.nchan = nchan
        self.nsam = nsam
        self.run_forever = run_forever
        if aochan == 0:
            aochan = nchan
        self.aw = np.zeros((nsam,aochan))
        for ch in range(0, aochan):
            self.aw[:,ch] = ch
        self.aw.astype('int16').tofile("awg.dat")
        self.current = np.zeros(nchan)
        self.finished = 0
        self.in_bounds = False
        self.KFB = gain
        self.passvalue = passvalue/gain 
        self.identity_pattern = bool(int(os.getenv("IDENTITY_PATTERN", 0)))
        self.verbose = int(os.getenv("VERBOSE", 0))
        self.ao0 = ao0
        self.user_quit = False
        self.defs = AwgDefaults(uut.uut)
        # offsets compensate channel geometry when AWG disabled
        self.apply_geometry = bool(int(os.getenv("AO_CORRECT_GEOMETRY", 0)))
        self.geometry = [ 
            -2*3.3, 0, 0, -2*3.3, 0, 0, 0, 6*3.3, 
                0, 0, 0, 0, 0, -3*3.3, 0, 0,
                -2*3.3, 0, 0, -2*3.3, 0, 0, 0, 6*3.3, 
                0, 0, 0, 0, 0, -3*3.3, 0, 0
        ]

        try:
            print("self.identity_pattern {}".format(self.identity_pattern))
            if not self.identity_pattern:
                self.current = self.defs.read_defaults()
                for ch in range(0, self.nchan):            
                    self.aw[:,self.ao0+ch] = self.current[ch]

        except IOError:
            print("no defaults")

    def vprint(self, str):
        if self.verbose > 0:
            print(str)

    def feedback(self, fb_data):
        actual = np.mean(fb_data[50:,:], 0)
        errmax = max(abs(actual))
        if  errmax < self.passvalue:
            print("maximum error {} is within bounds {}, save it".format(errmax, self.passvalue))
            self.defs.store_defaults(self.current)
            self.in_bounds = True
        else:
            print("maximum error {}".format(errmax))

        self.current = np.mean(self.aw, 0)[self.ao0:self.ao0+self.nchan]
        newset = self.current - actual * self.KFB
        print("newset {}".format(newset))        
        if not self.identity_pattern:
            for ch in range(0, self.nchan):            
                self.aw[:,self.ao0+ch] = newset[ch]

        self.aw.astype('int16').tofile("awg.dat")


    def load(self, autorearm = False):
        self.vprint("load 01")
        yy = self
        while not self.finished or not self.user_quit:
            self.vprint("load 10")
            if self.finished and self.apply_geometry:
                print("apply_geometry")
                for ch in range(0, self.nchan):
                    self.aw[:,ch] += self.geometry[ch]
                yy = None
            self.uut.load_awg(self.aw.astype(np.int16), autorearm = autorearm)           
            print("loaded array ", self.aw.shape)
            if self.in_bounds:
                # plot this one, drop out next time
                print("Target achieved, quit any time")
                self.finished = True
            self.vprint("load 66")
            yield yy

        self.vprint("load 99")



