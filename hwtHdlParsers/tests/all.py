#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from unittest import TestLoader, TextTestRunner, TestSuite
from hwtHdlParsers.tests.test_hierarchyExtractor import HierarchyExtractorTC
from hwtHdlParsers.tests.test_parser import ParserTC
from hwtHdlParsers.tests.test_verilogCodesign import VerilogCodesignTC
from hwtHdlParsers.tests.test_vhdlCodesign import VhdlCodesignTC

if __name__ == "__main__":
    def testSuiteFromTCs(*tcs):
        loader = TestLoader()
        loadedTcs = [loader.loadTestsFromTestCase(tc) for tc in tcs]
        suite = TestSuite(loadedTcs)
        return suite

    suite = testSuiteFromTCs(
        HierarchyExtractorTC,
        ParserTC,
        VerilogCodesignTC,
        VhdlCodesignTC
    )
    runner = TextTestRunner(verbosity=2)
    runner.run(suite)
