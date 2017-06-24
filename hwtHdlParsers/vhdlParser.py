from hwt.hdlObjects.operatorDefs import AllOps
from hwt.synthesizer.rtlLevel.mainBases import RtlSignalBase
from hwtHdlParsers.baseParser import BaseParser


def pushBit(v, b):
    return (v << 1) | b


def parseVhdlBitString(val, toType):
    v = val.clone()
    _v = v.val
    v.val = 0
    v.vldMask = 0
    v._dtype = toType
    for ch in reversed(_v):
        if ch == '1':
            v.val = pushBit(v.val, 1)
            v.vldMask = pushBit(v.vldMask, 1)
        elif ch == '0':
            v.val = pushBit(v.val, 0)
            v.vldMask = pushBit(v.vldMask, 1)
        elif ch == 'x':
            v.val = pushBit(v.val, 0)
            v.vldMask = pushBit(v.vldMask, 0)
        else:
            raise TypeError("found %s in bitstring literal" % (ch))
    return v


class VhdlParser(BaseParser):

    def opFromJson(self, jOp, ctx):
        operator = AllOps.opByName(jOp['operator'])
        op0 = self.exprFromJson(jOp['op0'], ctx)
        ops = [op0]
        if operator == AllOps.TERNARY or operator == AllOps.CALL:
            for jOperand in jOp['operands']:
                operand = self.exprFromJson(jOperand, ctx)
                ops.append(operand)
            if operator == AllOps.CALL and isinstance(ops[0], RtlSignalBase):
                operator = AllOps.INDEX
        else:
            if operator == AllOps.DOT:
                l = jOp['op1']['literal']
                assert l['type'] == "ID"
                ops.append(l['value'])
            else:
                ops.append(self.exprFromJson(jOp['op1'], ctx))
        return operator._evalFn(*ops)
