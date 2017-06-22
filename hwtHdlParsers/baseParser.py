#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parser is generated by antlr4, and is in C++ because in Python it is incredibly slow (20min vs 0.2s)

https://github.com/antlr/antlr4/blob/master/doc/getting-started.md
https://github.com/antlr/antlr4
https://github.com/antlr/grammars-v4/blob/master/vhdl/vhdl.g4
https://github.com/loranbriggs/Antlr/blob/master/The%20Definitive%20ANTLR%204%20Reference.pdf
"""

from hwt.hdlObjects.architecture import Architecture
from hwt.hdlObjects.assignment import Assignment
from hwt.hdlObjects.constants import Unconstrained
from hwt.hdlObjects.entity import Entity
from hwt.hdlObjects.operatorDefs import AllOps
from hwt.hdlObjects.portItem import PortItem
from hwt.hdlObjects.statements import IfContainer, WhileContainer
from hwt.hdlObjects.typeShortcuts import hInt, vec
from hwt.hdlObjects.types.bits import Bits
from hwt.hdlObjects.types.defs import STR
from hwt.synthesizer.param import Param
from hwtHdlParsers.hdlContexts import HDLParseErr
from hwtHdlParsers.hdlObjects.function import Function
from hwtHdlParsers.hdlObjects.hdlContext import HdlContext, RequireImportErr
from hwtHdlParsers.hdlObjects.package import PackageHeader, PackageBody
from hwtHdlParsers.hdlObjects.reference import HdlRef
from hwtHdlParsers.hdlObjects.returnStm import ReturnContainer


class ParserException(Exception):
    pass


class BaseParser(object):
    VERILOG = 'verilog'
    VHDL = 'vhdl'

    def __init__(self, caseSensitive, hierarchyOnly=False, primaryUnitsOnly=True):
        self.caseSensitive = caseSensitive
        self.hierarchyOnly = hierarchyOnly
        self.primaryUnitsOnly = primaryUnitsOnly

    def packageHeaderFromJson(self, jPh, ctx):
        ph = PackageHeader(jPh['name'], ctx)
        for jComp in jPh['components']:
            c = self.entityFromJson(jComp, ctx)
            ph.insertObj(c, self.caseSensitive)
        for jFn in jPh['functions']:
            fn = self.functionFromJson(jFn, ctx)
            ph.insertObj(fn, self.caseSensitive, hierarchyOnly=self.hierarchyOnly)
        # [TODO] types constants etc
        # if not self.hierarchyOnly:
        #    raise NotImplementedError()
        return ph

    def packageBodyFromJson(self, jPack, ctx):
        pb = PackageBody(jPack['name'], ctx)

        # [TODO] types constants etc
        for jFn in jPack['functions']:
            fn = self.functionFromJson(jFn, ctx)
            pb.insertObj(fn, self.caseSensitive, hierarchyOnly=self.hierarchyOnly)
        # if not self.hierarchyOnly:
        #    raise NotImplementedError()
        return pb

    def litFromJson(self, jLit, ctx):
            t = jLit['type']
            v = jLit['value']
            if t == 'ID':
                if isinstance(v[0], str):  # [TODO] not clear
                    ref = HdlRef([v], self.caseSensitive)
                else:
                    ref = self.hdlRefFromJson(v)
                v = ctx.lookupLocal(ref)
            elif t == 'INT':
                bits = jLit.get("bits", None)
                if bits is None:
                    v = hInt(v)
                else:
                    v = vec(v, bits)
            elif t == 'STRING':
                v = STR.fromPy(str(v))
            else:
                raise HDLParseErr("Unknown type of literal %s" % (t))
            return v

    def opFromJson(self, jOp, ctx):
        operator = AllOps.opByName(jOp['operator'])
        op0 = self.exprFromJson(jOp['op0'], ctx)
        ops = [op0]
        if operator == AllOps.TERNARY or operator == AllOps.CALL:
            for jOperand in jOp['operands']:
                operand = self.exprFromJson(jOperand, ctx)
                ops.append(operand)
        else:
            if operator == AllOps.DOT:
                l = jOp['op1']['literal']
                assert l['type'] == "ID"
                ops.append(l['value'])
            else:
                ops.append(self.exprFromJson(jOp['op1'], ctx))
        return operator._evalFn(*ops)

    def exprFromJson(self, jExpr, ctx):
        lit = jExpr.get("literal", None)
        if lit:
            return self.litFromJson(lit, ctx)

        binOp = jExpr['binOperator']
        if binOp:
            return self.opFromJson(binOp, ctx)

        raise HDLParseErr("Unparsable expression %s" % (str(jExpr)))

    def portFromJson(self, jPort, ctx, entity):
        v = jPort['variable']
        var_type = self.typeFromJson(v['type'], ctx)
        p = PortItem(v['name'], jPort['direction'], var_type, entity)
        val = v['value']
        if val is not None:
            p.defaultVal = self.exprFromJson(val, ctx)
        return p

    def typeFromJson(self, jType, ctx):
        try:
            t_name_str = jType['literal']['value']
        except KeyError:
            op = jType['binOperator']
            t_name = self.hdlRefFromJson(op['op0'])
            t = ctx.lookupLocal(t_name)
            specificator = self.exprFromJson(op['op1'], ctx)

            return t.applySpecificator(specificator)
        t_name = HdlRef([t_name_str], self.caseSensitive)
        return ctx.lookupLocal(t_name)

    def varDeclrJson(self, jVar, ctx):
        """parse generics, const arguments of functions etc.."""
        name = jVar['name']
        t = jVar["type"]
        t = self.typeFromJson(t, ctx)
        if isinstance(t, Bits) and isinstance(t.constrain, Unconstrained):
            try:
                t.constrain.derivedWidth = int(jVar['value']['literal']["bits"])
            except KeyError:
                pass
            except TypeError:
                pass
        v = jVar['value']
        if v is not None:
            defaultVal = self.exprFromJson(v, ctx)
            # convert it to t of variable (type can be different for example 1 as Natural or Integer)
            defaultVal = defaultVal._dtype.convert(defaultVal, t)
        else:
            defaultVal = t.fromPy(None)
        g = Param(defaultVal)
        g._dtype = t
        g.setHdlName(name)
        g._name = self._hdlId(name)
        return g

    def _hdlId(self, _id):
        if self.caseSensitive:
            return _id
        else:
            return _id.lower()

    def entityFromJson(self, jEnt, ctx):
        e = Entity(jEnt['name'])
        if not self.hierarchyOnly:
            entCtx = HdlContext(e.name, ctx)
            for jGener in jEnt['generics']:
                g = self.varDeclrJson(jGener, entCtx)
                e.generics.append(g)
                entCtx[g._name] = g

            # entCtx.update(ctx)
            for jPort in jEnt['ports']:
                p = self.portFromJson(jPort, entCtx, e)
                e.ports.append(p)

            e.generics.sort(key=lambda x: x.name)
            e.ports.sort(key=lambda x: x.name)
        return e

    def componentInstanceFromJson(self, jComp, ctx):
        ci = Entity(jComp['name'])
        ci.entityRef = self.hdlRefFromJson(jComp['entityName'])
        if not self.hierarchyOnly:
            pass
            # raise NotImplementedError()
            # [TODO] port, generics maps
        return ci

    def archFromJson(self, jArch, ctx):
        a = Architecture(None)
        a.entityName = jArch["entityName"]
        a.name = jArch['name']
        for jComp in jArch['componentInstances']:
            ci = self.componentInstanceFromJson(jComp, ctx)
            a.componentInstances.append(ci)
        if not self.hierarchyOnly:
            pass  # [TODO]
            # raise NotImplementedError()
        return a

    def statementFromJson(self, jStm, ctx):
        t = jStm['type']

        def expr(name):
            return self.exprFromJson(jStm[name], ctx)

        def stList(name):
            return [self.statementFromJson(x, ctx) for x in jStm[name]]

        if t == 'ASSIGMENT':
            src = expr('src')
            dst = expr('dst')
            return Assignment(src, dst)
        elif t == 'IF':
            cond = [expr('cond')]
            ifTrue = stList('ifTrue')
            ifFalse = stList('ifFalse')
            return IfContainer(cond, ifTrue, ifFalse)
        elif t == 'RETURN':
            return ReturnContainer(expr('val'))
        elif t == 'WHILE':
            cond = [expr('cond')]
            body = stList('body')
            return WhileContainer(cond, body)
        else:
            raise NotImplementedError(t)

    def functionFromJson(self, jFn, ctx):
        name = jFn['name']
        isOperator = jFn['isOperator']
        returnT = None
        params = []
        exprList = []
        _locals = []
        fnCtx = HdlContext(name, ctx)
        if not self.hierarchyOnly:
            returnT = self.typeFromJson(jFn['returnT'], fnCtx)

            for jP in jFn['params']:
                p = self.varDeclrJson(jP, fnCtx)
                params.append(p)
                fnCtx.insertObj(p, self.caseSensitive, self.hierarchyOnly)

            for jL in jFn['locals']:
                l = self.varDeclrJson(jL, fnCtx)
                _locals.append(l)
                fnCtx.insertObj(l, self.caseSensitive, self.hierarchyOnly)

            for jStm in jFn['body']:
                exprList.append(self.statementFromJson(jStm, fnCtx))

        return Function(name, returnT, fnCtx, params, _locals, exprList, isOperator)

    def hdlRefFromJson(self, jsn):
        def flattern(jsn, op):
            try:
                binOp = jsn['binOperator']
            except KeyError:
                yield jsn['literal']
                raise StopIteration()
            if binOp['operator'] == op:
                yield from flattern(binOp['op0'], op)
                yield from flattern(binOp['op1'], op)
            else:
                yield binOp
        allChilds = False
        names = []
        # [TODO]
        for j in flattern(jsn, 'DOT'):
            t = j["type"]
            if t == 'ID' or t == "STRING":
                names.append(j['value'])
            elif t == "ALL":
                allChilds = True
            else:
                raise NotImplementedError("Not implemented for id part of type %s" % (t))
        return HdlRef(names, self.caseSensitive, allChilds=allChilds)

    def parse(self, jsonctx, fileName, ctx):
        """
        @param fileName: vhdl filename
        @param ctx: parent HDL context
        @param hierarchyOnly: discover only presence of entities, architectures
                and component instances inside, packages and components inside, packages
        @param primaryUnitsOnly: parse only entities and package headers
        """
        dependencies = set()
        try:
            for jsnU in jsonctx['imports']:
                u = self.hdlRefFromJson(jsnU)
                dependencies.add(u)
                # if ctx.lookupGlobal(u) is None:
                if not self.hierarchyOnly:
                    ctx.importLibFromGlobal(u)
        except RequireImportErr as e:
            e.fileName = fileName
            raise e

        for jPh in jsonctx["packageHeaders"]:
            ph = self.packageHeaderFromJson(jPh, ctx)
            n = self._hdlId(ph.name)
            if n not in ctx.packages:
                ctx.insertObj(ph, self.caseSensitive)
            else:
                ctx.packages[n].update(ph)

        for jE in jsonctx["entities"]:
            ent = self.entityFromJson(jE, ctx)
            ent.parent = ctx
            ent.dependencies = dependencies
            ctx.insertObj(ent, self.caseSensitive)

        if not self.primaryUnitsOnly:
            for jpBody in jsonctx["packages"]:
                pb = self.packageBodyFromJson(jpBody, ctx)
                n = self._hdlId(pb.name)
                if n not in ctx.packages:
                    ph = PackageHeader(n, ctx, isDummy=True)
                    ph.insertBody(pb)
                    ctx.insertObj(ph, self.caseSensitive)
                else:
                    ctx.packages[n].insertBody(pb)
            for jArch in jsonctx['architectures']:
                arch = self.archFromJson(jArch, ctx)
                arch.parent = ctx
                arch.dependencies = dependencies
                ctx.insertObj(arch, self.caseSensitive)
