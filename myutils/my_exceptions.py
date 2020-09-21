MY_EXCEPTION_CODE_UNK = -100


class MyException(Exception):

    def __init__(self, message, ncode, reason, *args):
        super().__init__(message, *args)
        self.code = ncode
        self.reason = reason

    def __init__(self, message, ncode, *args):
        super().__init__(message, *args)
        self.code = ncode
        self.reason = None


    def __str__(self) -> object:
        s: str = super().__str__()
        if s is None:
            s = ""
        if isinstance(self.code, int):
            s = s + " NCODE={:d}".format(self.code)
        if self.reason is not None:
            sc = self.reason.__class__
            s = s + \
                " BY " + sc.__name__ + \
                ":" + self.reason.__str__()
        return s

    def getcode(self):
        return self.code

