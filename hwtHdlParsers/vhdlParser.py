from hwt.hdlObjects.operatorDefs import AllOps
from hwt.synthesizer.rtlLevel.mainBases import RtlSignalBase
from hwtHdlParsers.baseParser import BaseParser


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
