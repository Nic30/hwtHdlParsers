import unittest

from hdl_toolkit.hdlObjects.typeShortcuts import hInt
from hdl_toolkit.interfaces.all import allInterfaces
from hwtHdlParsers.tests.baseSynthesizerTC import VERILOG_DIR
from hwtHdlParsers.unitFromHdl import UnitFromHdl
from hwtLib.interfaces.amba import Axi4_xil
from hwtLib.tests.synthesizer.interfaceLevel.baseSynthesizerTC import BaseSynthesizerTC


class VerilogCodesignTC(BaseSynthesizerTC):
    def test_TernOpInModul(self):
        class TernOpInModulSample(UnitFromHdl):
            _hdlSources = VERILOG_DIR + "ternOpInModul.v"
            _debugParser = True
                    
        u = TernOpInModulSample()
        u._loadDeclarations()
        
        self.assertEquals(u.a._dtype.bit_length(), 8)
        self.assertEquals(u.b._dtype.bit_length(), 1)
        
        u.CONDP.set(hInt(1))
        self.assertEquals(u.a._dtype.bit_length(), 4)
        self.assertEquals(u.b._dtype.bit_length(), 2)
        
    def test_SizeExpressions(self):
        class SizeExpressionsSample(UnitFromHdl):
            _hdlSources = VERILOG_DIR + "sizeExpressions.v"        
        u = SizeExpressionsSample()
        u._loadDeclarations()
        
        A = u.paramA.get()
        B = u.paramB.get()
        self.assertEqual(u.portA._dtype.bit_length(), A.val)
        self.assertEqual(u.portB._dtype.bit_length(), A.val)
        self.assertEqual(u.portC._dtype.bit_length(), A.val // 8)
        self.assertEqual(u.portD._dtype.bit_length(), (A.val // 8) * 13)
        self.assertEqual(u.portE._dtype.bit_length(), B.val * (A.val // 8))
        self.assertEqual(u.portF._dtype.bit_length(), B.val * A.val)
        self.assertEqual(u.portG._dtype.bit_length(), B.val * (A.val - 4))
    
    def test_InterfaceArray(self):
        class InterfaceArraySample(UnitFromHdl):
            _hdlSources = VERILOG_DIR + "interfaceArrayAxiStream.v"        
        u = InterfaceArraySample()
        u._loadDeclarations()
        
        self.assertEqual(u.input_axis.DATA_WIDTH.get().val, 32)
        self.assertEqual(u.input_axis._multipliedBy, u.LEN)
    
    
    def test_InterfaceArray2(self):
        class InterfaceArraySample(UnitFromHdl):
            _hdlSources = VERILOG_DIR + "interfaceArrayAxi4.v"
            _intfClasses = [Axi4_xil] + allInterfaces        
        u = InterfaceArraySample()
        u._loadDeclarations()
        
        self.assertEqual(u.m_axi._multipliedBy, u.C_NUM_MASTER_SLOTS)
        self.assertEqual(u.s_axi._multipliedBy, u.C_NUM_SLAVE_SLOTS)
    
    def test_paramSpecifiedByParam(self):
        class U(UnitFromHdl):
            _hdlSources = VERILOG_DIR + "parameterSizeFromParameter.v"        
        u = U()
        u._loadDeclarations()
        
        self.assertEqual(u.A.get(), hInt(1))
        self.assertEqual(u.B.get(), hInt(2))
        
        
        self.assertEqual(u.aMultBMult64._dtype.bit_length(), 1 * 2 * 64)
        self.assertEqual(u.aMult32._dtype.bit_length(), 1 * 32)
        
    
    def test_axiCrossbar(self):
        class U(UnitFromHdl):
            _hdlSources = VERILOG_DIR + "axiCrossbar.v"
            _intfClasses = [Axi4_xil] + allInterfaces 
        u = U()
        u._loadDeclarations()
        
        self.assertEqual(u.s_axi._multipliedBy, u.C_NUM_SLAVE_SLOTS)
        self.assertEqual(u.m_axi._multipliedBy, u.C_NUM_MASTER_SLOTS)
        
    
if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(VerilogCodesignTC('test_InterfaceArray2'))
    suite.addTest(unittest.makeSuite(VerilogCodesignTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
