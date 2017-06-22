from copy import copy
import inspect, os
import types

from hwt.hdlObjects.constants import INTF_DIRECTION, Unconstrained
from hwt.hdlObjects.entity import Entity
from hwt.hdlObjects.operator import Operator
from hwt.hdlObjects.portItem import PortItem
from hwt.hdlObjects.value import Value
from hwt.synthesizer.interfaceLevel.interfaceUtils.utils import walkPhysInterfaces
from hwt.synthesizer.interfaceLevel.unit import Unit
from hwt.synthesizer.interfaceLevel.unitUtils import defaultUnitName
from hwt.synthesizer.param import Param
from hwt.synthesizer.rtlLevel.mainBases import RtlSignalBase
from hwt.synthesizer.uniqList import UniqList
from hwtHdlParsers.hdlObjects.function import Function
from hwtHdlParsers.hdlObjects.hdlContext import RequireImportErr
from hwtHdlParsers.utils import entityFromFile, loadCntxWithDependencies


def cloneExprWithUpdatedParams(expr, paramUpdateDict):
    if isinstance(expr, Param):
        return paramUpdateDict[expr]
    elif isinstance(expr, Value):
        return expr.clone()
    elif isinstance(expr, RtlSignalBase):
        d = expr.singleDriver()
        assert isinstance(d, Operator)
        ops = [ cloneExprWithUpdatedParams(x, paramUpdateDict) for x in d.ops]
        return Operator.withRes(d.operator, ops, d.result._dtype)
    elif isinstance(expr, Function):
        return expr
    elif isinstance(expr, Unconstrained):
        return copy(expr)
    else:
        raise NotImplementedError("Not implemented for %s" % (repr(expr)))

def toAbsolutePaths(relativeTo, sources):
    paths = UniqList()
    
    if isinstance(sources, str):
        sources = [sources]
    

    def collectPaths(p):
        if isinstance(p, str):
            _p = os.path.join(relativeTo, p)
            paths.append(_p)
        elif isinstance(p, type) and issubclass(p, UnitFromHdl):
            p._buildFileNames()
            for _p in p._hdlSources:
                paths.append(_p)
        else:
            # tuple (lib, filename)
            _p = (p[0], os.path.join(relativeTo, p[1]))
            paths.append(_p)
    
    for s in sources:
        collectPaths(s)
    
    return paths 

class UnitFromHdl(Unit):
    """
    @cvar _hdlSources:  str or list of hdl filenames, they can be relative to file 
        where is *.py file stored and they are automaticaly converted to absolute path
        first entity in first file is taken as interface template for this unit
        this is currently supported only for vhdl
    @cvar _intfClasses: interface classes which are searched on hdl entity 
    @cvar _debugParser: flag to run hdl parser in debug mode
    """
    def __init__(self):
        self._builded()
        super(UnitFromHdl, self).__init__()
    
    def _config(self):
        cls = self.__class__
        self._params = []
        self._interfaces = []
        self._paramsOrigToInst = {}

        for p in cls._params:
            instP = Param(p.defaultVal)
            setattr(self, p.name, instP)
            instP.hasGenericName = False
            
    def _declr(self):
        cls = self.__class__
        for p in cls._params:
            self._paramsOrigToInst[p] = getattr(self, p.name)
            
        for i in cls._interfaces:
            instI = i.__class__(loadConfig=False)
            instI._isExtern = i._isExtern 
            instI._origI = i
            def configFromExtractedIntf(instI):
                for p in instI._origI._params:
                    if p.replacedWith:
                        pName = p.replacedWith.name
                        instP = getattr(self, pName)
                        setattr(instI, p.name, instP)
                    else:
                        # parameter was not found
                        instV = p.defaultVal.clone()
                        instV.vldMask = 0
                        setattr(instI, p.name, Param(instV))
                
  
                             
            # overload _config function
            instI._config = types.MethodType(configFromExtractedIntf, instI)
            instI._loadConfig()
                  
            instI._origLoadDeclarations = instI._loadDeclarations
            def declarationsFromExtractedIntf(instI):
                instI._origLoadDeclarations()
                instI._setDirectionsLikeIn(instI._origI._direction)
                
                # set array size
                mulBy = instI._origI._multipliedBy
                if isinstance(mulBy, Param):
                    mulBy = self._paramsOrigToInst[mulBy]
                instI._setMultipliedBy(mulBy)  
                
                for iSig, instISig in zip(walkPhysInterfaces(instI._origI), walkPhysInterfaces(instI)):
                    instISig._originEntityPort = iSig._originEntityPort  # currently used only for name
                    if not iSig._dtypeMatch:
                        origT = iSig._originEntityPort._dtype
                        newT = copy(origT)
                        if origT.constrain is not None:
                            newT.constrain = cloneExprWithUpdatedParams(origT.constrain, self._paramsOrigToInst)  
                        instISig._dtype = newT
            # overload _loadDeclarations function
            instI._loadDeclarations = types.MethodType(declarationsFromExtractedIntf, instI) 
            
            setattr(self, i._name, instI)
    
    @classmethod
    def _buildFileNames(cls):
        # convert source filenames to absolute paths
        assert cls._hdlSources
        baseDir = os.path.dirname(inspect.getfile(cls))
        cls._hdlSources = toAbsolutePaths(baseDir, cls._hdlSources)
    
    @staticmethod
    def _loadEntity(cls, ignoreCache=False):
        if not hasattr(cls, "_debugParser"):
            cls._debugParser = False
        # extract params from entity generics
        try:
            return entityFromFile(cls._hdlSources[0], debug=cls._debugParser)
        except RequireImportErr:
            ctx = loadCntxWithDependencies(cls._hdlSources, debug=cls._debugParser)
            for _, e in ctx.entities.items():
                if e.parent == ctx:
                    return e
    
    @classmethod
    def _isBuild(cls):
        try:
            return cls._clsBuildFor == cls
        except AttributeError:
            return False
        
    @classmethod
    def _builded(cls):
        if not cls._isBuild():
            cls._build()   
        
    @classmethod
    def _build(cls):
        cls._buildFileNames()
        
        # init hdl object containers on this unit       
        cls._params = []
        cls._interfaces = []
        cls._units = []

        cls._entity = cls._loadEntity(cls)
            
        for g in cls._entity.generics:
            cls._params.append(g)

        # lookup all interfaces
        for intfCls in cls._intfClasses:
            for intfName, interface in intfCls._tryToExtract(cls._entity.ports):
                interface._name = intfName
                cls._interfaces.append(interface)
                interface._setAsExtern(True)

        for p in cls._entity.ports:
            # == loading testbenches is not supported by this class 
            if not (hasattr(p, '_interface') and p._interface is not None):
                # every port should have interface (Signal at least) 
                raise AssertionError("Port %s does not have any interface assigned" % (p.name))  
  
        
        cls._clsBuildFor = cls
    
    def _toRtl(self):
        """Convert unit to hdl objects"""
        
        if not hasattr(self, '_name'):
            self._name = defaultUnitName(self)
        self._loadMyImplementations()
        self._entity = Entity(self.__class__._entity.name)
        self._entity._name = self._name
        
        generics = self._entity.generics
        ports = self._entity.ports
        
        for p in self._params:
            generics.append(p)
        
        for unitIntf in self._interfaces:
            for i in walkPhysInterfaces(unitIntf):
                pi = PortItem(i._getPhysicalName(), INTF_DIRECTION.asDirection(i._direction), i._dtype, self._entity)
                pi._interface = i
                ports.append(pi)
                i._originEntityPort = pi
            
        return [self]

    def _wasSynthetised(self):
        return True
    
    def asVhdl(self, serializer):
        return str(self)
    
    def __str__(self):
        return "\n".join(['--%s' % (repr(s)) for s in self._hdlSources])
