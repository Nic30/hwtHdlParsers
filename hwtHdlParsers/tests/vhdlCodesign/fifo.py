from hwt.interfaces.std import Clk, Rst_n
from hwt.interfaces.std import FifoReader, FifoWriter 
from hwt.synthesizer.shortcuts import toRtl
from hwtHdlParsers.unitFromHdl import UnitFromHdl


class Fifo(UnitFromHdl):
    _hdlSources = ["vhdl/fifo.vhd"]
    _intfClasses = [FifoWriter, FifoReader, Clk, Rst_n]


if __name__ == "__main__":
    u = Fifo()
    print(toRtl(u))
    print(u._entity)
