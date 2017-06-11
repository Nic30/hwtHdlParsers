from hwtHdlParsers.unitFromHdl import UnitFromHdl


class SimpleUnit_FromVhdl(UnitFromHdl):
    _hdlSources = 'vhdl/simplest_b.vhd'

if __name__ == "__main__":
    from hwt.synthesizer.shortcuts import toRtl
    print(toRtl(SimpleUnit_FromVhdl))
