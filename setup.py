#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from setuptools import setup, find_packages

setup(name='hwtHdlParsers',
      version='0.1',
      description='(System) Verilog, VHDL compatibility layer for HWToolkit library',
      url='https://github.com/Nic30/hwtHdlParsers',
      author='Michal Orsak',
      author_email='michal.o.socials@gmail.com',
      install_requires=[
        'hwtoolkit',
        'hwtLib'
      ],
      license='MIT',
      packages = find_packages(),
      zip_safe=False)
