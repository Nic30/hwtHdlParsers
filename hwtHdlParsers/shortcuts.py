import hdlConvertor
from itertools import chain

from hdl_toolkit.synthesizer.interfaceLevel.unit import Unit
from hdl_toolkit.synthesizer.interfaceLevel.unitUtils import defaultUnitName
from hdl_toolkit.synthesizer.shortcuts import toRtlAndSave
from hwtHdlParsers.loader import langFromExtension, ParserFileInfo
from hwtHdlParsers.unitFromHdl import UnitFromHdl
from python_toolkit.fileHelpers import find_files


def fileSyntaxCheck(fileInfo, timeoutInterval=20):
    """
    Perform syntax check on whole file
    """
    return hdlConvertor.parse(fileInfo.fileName, fileInfo.lang) 


def _syntaxCheckUnitFromHdl(u):
    for f in u._hdlSources:
        if isinstance(f, str):
            fi = ParserFileInfo(f, 'work')
        else:
            fi = ParserFileInfo(f[1], f[0])
        fileSyntaxCheck(fi)


def syntaxCheck(unitOrFileName):
    if issubclass(unitOrFileName, UnitFromHdl):
        unitOrFileName._buildFileNames()
        _syntaxCheckUnitFromHdl(unitOrFileName)
        
    elif isinstance(unitOrFileName, UnitFromHdl):
        _syntaxCheckUnitFromHdl(unitOrFileName)
    elif isinstance(unitOrFileName, Unit):
        try:
            unitName = unitOrFileName._name
        except AttributeError:
            unitName = defaultUnitName(unitOrFileName)
        
        d = "__pycache__/" + unitName
        toRtlAndSave(unitOrFileName, d)
        for f in chain(find_files(d, '*.vhd', recursive=True), find_files(d, '*.v', recursive=True)):
            fileSyntaxCheck(ParserFileInfo(d, 'work'))
        
    elif isinstance(unitOrFileName, str):
        fileSyntaxCheck(f, langFromExtension(unitOrFileName))
    else:
        raise  NotImplementedError("Not implemented for '%'" % (repr(unitOrFileName)))
    