#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from myhdl.conversion._toVHDL import _shortversion

from hwt.hdlObjects.functionContainer import FunctionContainer
from hwt.hdlObjects.types.bits import Bits
from hwt.hdlObjects.types.defs import BOOL, INT, STR, BIT
from hwt.hdlObjects.types.integer import Integer
from hwtHdlParsers.hdlObjects.hdlContext import HdlContext
from hwtHdlParsers.hdlObjects.reference import HdlRef 


class HDLParseErr(Exception):
    pass


class FakeStd_logic_1164():
    """mock of Std_logic_1164 from vhdl"""
    std_logic_vector = Bits(forceVector=True)
    std_logic_vector_ref = HdlRef(["ieee", "std_logic_1164", "std_logic_vector"], False)
    std_ulogic_vector_ref = HdlRef(["ieee", "std_logic_1164", "std_ulogic"], False)
    
    std_logic_unsigned_sub_ref = HdlRef(["ieee", "std_logic_unsigned", "-"], False)
    std_logic_unsigned_sub = FunctionContainer('-', None)

    std_logic = BIT
    std_logic_ref = HdlRef(["ieee", "std_logic_1164", "std_logic"], False)
    
    signed_ref = HdlRef(["ieee", "numeric_std", 'signed'], False)
    signed = Bits(signed=True)

    unsigned_ref = HdlRef(["ieee", "numeric_std", 'unsigned'], False)
    unsigned = Bits(signed=False)
    
    resize_ref = HdlRef(["ieee", "numeric_std", 'resize'], False)
    resize = FunctionContainer('resize', None)

class FakeMyHdl():
    p_name = "pck_myhdl_%s" % _shortversion
    package_ref = HdlRef(["work", p_name ], False)
    package_fake = HdlContext(p_name, None)

class BaseVhdlContext():
    integer = INT
    natural = Integer(_min=0)
    positive = Integer(_min=1)
    boolean = BOOL
    string = STR
    
   
    @classmethod
    def importFakeLibs(cls, ctx):
        BaseVhdlContext.importFakeIEEELib(ctx)
        BaseVhdlContext.importFakeTextIo(ctx)
        ctx.insert(FakeMyHdl.package_ref, FakeMyHdl.package_fake)
        
    @classmethod
    def importFakeTextIo(cls, ctx):
        ctx.insert(HdlRef(['std', 'textio', 'read'], False), None)

    @classmethod 
    def importFakeIEEELib(cls, ctx):
        f = FakeStd_logic_1164
        ctx.insert(f.std_logic_vector_ref, f.std_logic_vector)
        ctx.insert(f.std_ulogic_vector_ref, f.std_logic_vector)
        ctx.insert(f.std_logic_ref, f.std_logic)
        ctx.insert(HdlRef(['ieee', 'std_logic_unsigned', 'conv_integer'], False), None)
        ctx.insert(HdlRef(['ieee', 'std_logic_arith', 'is_signed'], False), None)
        ctx.insert(HdlRef(["ieee", "std_logic_misc", "and_reduce"], False), None)
        ctx.insert(f.std_logic_unsigned_sub_ref, f.std_logic_unsigned_sub)
        ctx.insert(f.signed_ref, f.signed)
        ctx.insert(f.unsigned_ref, f.unsigned)
        ctx.insert(f.resize_ref, f.resize)
    
    @classmethod
    def getBaseCtx(cls):
        d = HdlContext(None, None)
        d['integer'] = cls.integer
        d['positive'] = cls.positive
        d['natural'] = cls.natural
        d['boolean'] = cls.boolean
        d['string'] = cls.string
        d['true'] = BOOL.fromPy(True)
        d['false'] = BOOL.fromPy(False)
        return d

class BaseVerilogContext():
    integer = INT
    string = STR
    wire = Bits()
   
    @classmethod
    def importFakeLibs(cls, ctx):
        pass

    @classmethod
    def getBaseCtx(cls):
        d = HdlContext(None, None)
        d['integer'] = cls.integer
        d['__str__'] = cls.string
        d['wire'] = cls.wire
        return d
