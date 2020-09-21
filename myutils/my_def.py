import sys
import abc

from myutils.my_exceptions import MyException
import logging

logger = logging.getLogger(__name__)

THIS_MODULE = 'my_def'

TOOL_FACTORY_MODULE_ARG = 'toolFactoryModule'
TOOL_FACTORY_CLASS_ARG='toolFactoryClass'

class MyArgsExe(abc.ABC):

    @classmethod
    @abc.abstractmethod
    def create_instance(cls, **args):
        pass

    @abc.abstractmethod
    def release(self):
        pass

    @abc.abstractmethod
    def exe_args(self, **args):
        pass

    @abc.abstractmethod
    def create_exe_instance(self, **args):
        pass


def strName2Class(modulename, classname):
    try:
        __import__(modulename)
        return getattr(sys.modules[modulename], classname)
    except Exception as ex:
        strmsg = 'Ошибка при получении класса по имени {:s}'.format(classname)
        raise MyException(strmsg,-200,ex)
    except BaseException as ex:
        strmsg = 'Ошибка злая при получении класса по имени {:s}'.format(
            classname)
        raise MyException(strmsg,-200,ex)


class MyToolFactory(object):

    def __init__(self):
        pass


    def create_obj_exe(self,  **args) -> MyArgsExe:
        if args is None:
            return None
        modulename = args.get(TOOL_FACTORY_MODULE_ARG)
        if (modulename is None):
            raise MyException("Не указан исполняющий модуль " +
                              TOOL_FACTORY_MODULE_ARG,
                              -200)
        toolname = args.get(TOOL_FACTORY_CLASS_ARG)
        if (toolname is None):
            raise MyException("Не указан исполняющий класс " +
                              TOOL_FACTORY_CLASS_ARG,
                              -200)
        toolClass = strName2Class(modulename, toolname)
        tool = toolClass.create_instance(**args)

        if isinstance(tool, MyArgsExe):
            toolexe: MyArgsExe = tool
            return toolexe

        raise MyException('Не исполнялка это ' + toolname,
                          ncode=-200)


if __name__ == "main":
    logger.info(THIS_MODULE + ' as main')
else:
    logger.info(THIS_MODULE + ' imported')