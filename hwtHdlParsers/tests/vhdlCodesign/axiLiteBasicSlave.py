from hwt.interfaces.std import Rst_n, Clk
from hwtHdlParsers.unitFromHdl import UnitFromHdl
from hwtLib.amba.axiLite import AxiLite


class AxiLiteBasicSlave(UnitFromHdl):
    _hdlSources = "vhdl/axiLite_basic_slave.vhd"
    _intfClasses = [Clk, Rst_n, AxiLite]
    
if __name__ == "__main__":
    from hwt.synthesizer.shortcuts import toRtl
    u = AxiLiteBasicSlave()
    print(toRtl(u))
    