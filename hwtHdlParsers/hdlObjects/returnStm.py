
class ReturnCalled(Exception):
    """
    Exception which is used as return statement while executing of hdl functions
    """
    def __init__(self, val):
        self.val = val


class ReturnContainer():
    """
    Stuctural container of return statement in hdl
    """

    def __init__(self, val=None):
        self.val = val

    def seqEval(self):
        raise ReturnCalled(self.val.staticEval())
