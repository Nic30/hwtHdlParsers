from hdl_toolkit.interfaces.std import BramPort
from hdl_toolkit.synthesizer.shortcuts import toRtl
from hwtHdlParsers.unitFromHdl import UnitFromHdl


class Bram(UnitFromHdl):
    _hdlSources = ["vhdl/dualportRAM.vhd"]
    _intfClasses = [BramPort]

class BramSp(UnitFromHdl):
    _hdlSources = ["vhdl/singleportRAM.vhd"]
    _intfClasses = [BramPort]
    
if __name__ == "__main__":
    print(toRtl(Bram()))
