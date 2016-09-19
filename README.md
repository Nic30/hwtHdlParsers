# hwtHdlParsers
[![Build Status](https://travis-ci.org/Nic30/hwtHdlParsers.svg?branch=master)](https://travis-ci.org/Nic30/hwtHdlParsers)

(System) Verilog, VHDL compatibility layer for HWToolkit library

This module allows HWTlibrary to use vhdl/(system) verilog (=HDL as Hardware Decription Languages).
HDL objects are converted to standard HWToolkit represenation and they can be used as any other.

It means for example you can evalueate hdl function or search in netlist or architecture from python.

Main purpose is to import vhdl/verilog code to HWT designs. 
Interfaces (any HWT interface like predefined axi4 or any user interface) can be also extracted. 

Objects extracted from hdl difer only in serialization, they are not serialized again, just files are used.

There are **examples** in hwtHdlParsers tests.