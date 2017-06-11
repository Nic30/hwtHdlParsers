from hwtHdlParsers.unitFromHdl import UnitFromHdl


ws = "vhdl/fnImport/"

lib = [ws + "package0.vhd"]

class EntWithFnRequired(UnitFromHdl):
    _hdlSources = [ws + "ent.vhd"] + lib

 
if __name__ == "__main__":
    from hwt.synthesizer.shortcuts import toRtl
    u = EntWithFnRequired()
    u._loadDeclarations()
    print(u)
    print(u.sig._dtype.bit_length())
    # print(toRtl(EntWithFnRequired))
