from hdl_toolkit.interfaces.std import Rst_n, Clk
from hwtHdlParsers.unitFromHdl import UnitFromHdl
from hwtLib.interfaces.amba import AxiLite_xil


class AxiLiteBasicSlave(UnitFromHdl):
    _hdlSources = "vhdl/axiLite_basic_slave.vhd"
    _intfClasses = [Clk, Rst_n, AxiLite_xil]
    
if __name__ == "__main__":
    from hdl_toolkit.synthesizer.shortcuts import toRtl
    u = AxiLiteBasicSlave()
    print(toRtl(u))
    