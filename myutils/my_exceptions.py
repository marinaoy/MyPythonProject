MY_EXCEPTION_CODE_UNK = -100


class MyException(Exception):

    def __init__(self, stext: str, ncode: int, exreason: Exception):
        """
        @type stext: str
        @type ncode: int
        @type exreason: Exception
        """
        self.text = stext
        self.code = ncode
        self.reason = exreason

    def __init__(self, stext: str, ncode: int):
        """
        @type stext: str
        @type ncode: int
        """
        self.text = stext
        self.code = ncode
        self.reason = None


    def __str__(self) -> object:
        s: str = super().__str__()
        if s is None:
            s = ""
        if isinstance(self.code, int):
            s = s + " NCODE={:d}".format(self.code)
        if isinstance(self.text, str):
            s = s + " text={:s}".format(self.text)
        if self.reason is not None:
            sc = self.reason.__class__
            s = s + \
                " BY " + sc.__name__ + \
                ":" + self.reason.__str__()
        return s

    def gettext(self):
        return self.text

    def getcode(self):
        return self.code
