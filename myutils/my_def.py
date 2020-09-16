import abc

import myutils.my_exceptions

TOOLKIT_ARG = 'toolkit'
TOOLNAME_ARG = 'toolname'

class MyArgsExe(abc.ABC):

    @abc.abstractmethod
    def release(self):
        pass

    @abc.abstractmethod
    def exe_args(self, **args):
        pass

    @abc.abstractmethod
    def create_instance(self, **args):
        pass


class MyToolFactory(object):

    def __init__(self):
        pass


    def create_obj_exe(self, **args) -> MyArgsExe:
        if args is None:
            return None
        toolkit = args.get(TOOLKIT_ARG)
        if toolkit is None:
            raise myutils.MyException(stext='Не определены исполнялки вообще',
                              ncode=-200)
        toolname =  args.get(TOOLNAME_ARG)
        if (toolname is None):
            raise myutils.MyException(stext='Не заказана исполнялка',
                                      ncode=-200)
        tool = toolkit.get(toolname)
        if tool is None:
            raise myutils.MyException(stext='Не определена исполнялка ' +
                                            toolname,
                              ncode=-200)
        if isinstance(tool, MyArgsExe):
            toolexe: MyArgsExe = tool
            return toolexe.create_instance(**args)

        raise myutils.MyException(stext='Не исполнялка это' + toolname,
                          ncode=-200)
