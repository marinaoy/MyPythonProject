import sys
import abc
import json
import datetime
import traceback
# import numpy as np

import pandas as pd

from collections import OrderedDict

from myutils.my_data_readers import readDataFrame
from myutils.my_exceptions import MyException as MyException
import logging

logger = logging.getLogger(__name__)

EX_CONFIG_NONE = -200
EX_CONFIG_INVALID = -201
EX_TOOL_NONE = -202
EX_CLASS = -203
EX_CONFIG_NO_DATA = -300
EX_CONFIG_NO_TOOLS = -310
EX_V_OCHERED = -1000

MAIN_CONFIG_KEY = 'main_config'

MODULE_ARG = 'tool_module'
CLASS_ARG = 'tool_class'

CFG_KEY_TOOLS = 'tools'
CFG_KEY_DATA = 'data'
CFG_KEY_APPLY_LIST = 'apply_tools_list'

DATA_SRC_FRAMES_KEY = 'data_frames'
DATA_FILE_NAME = 'data_file'
DATA_FILE_KEY = 'data_key'
DATA_KEY_READER = 'data_reader'
DATA_FRAMES_KEYS = 'df_keys'
DATA_FRAMES_TABLES = 'df_frames'

DATA_SRC_KEY = 'src_data'

TOOLS_FILE_NAME = 'tools_file'
TOOLS_FILE_KEY = 'tools_key'

RESULT_SRC_DATA_KEY = 'src_data'


# noinspection PyPep8Naming
def getResourceMsg(s: str) -> str:
    """

    @type s: str
    @rtype: str
    """
    # TODO получение строки из ресурсов
    return s


# noinspection PyPep8Naming
def strName2Class(modulename, classname, asClass):
    # получение класса по имени с возможной проверкой соответствия классу
    try:
        __import__(modulename)
        nClass = getattr(sys.modules[modulename], classname)
        if asClass is not None:
            if not (issubclass(nClass, asClass)):
                raise MyException(getResourceMsg("MSG:{0} class is "
                                                 "expected").format(
                    asClass), EX_CLASS)
        return nClass
    except Exception as ex:
        strmsg = getResourceMsg('MSG:Exception on access class by name {0} '
                                '\\ {1}').format(modulename, classname)
        raise MyException(strmsg, EX_CLASS, ex)
    except BaseException as ex:
        strmsg = getResourceMsg('MSG:BaseException on access class by name {'
                                '0} \\ {1}').format(modulename, classname)
        raise MyException(strmsg, EX_CLASS, ex)


class WaitDataException(Exception):
    def __init__(self, waitList:list, *args: object) -> None:
        super().__init__(*args)
        if waitList is not None:
            self.waitList = list(waitList)
        else:
            self.waitList = []

    def getWaitList(self):
        return self.waitList




# noinspection PyPep8Naming
class ToolJsonConfigReader(object):
    # noinspection PyPep8Naming
    def __init__(self, fileConfigName: str, mainKey: str = MAIN_CONFIG_KEY):
        self.fileConfigName = fileConfigName
        self.mainkey = mainKey

    def readMainConfig(self) -> dict:
        with open(self.fileConfigName, 'r', encoding='utf-8') as f:
            dictConfig = json.load(f)

        configName = dictConfig.get(self.mainkey)
        try:
            if configName is None:
                sMsg = getResourceMsg("MSG:Config name is not defined by {0}")
                raise MyException(sMsg.format(self.mainkey), EX_CONFIG_INVALID)
            configMain = dictConfig.get(configName)
            dictConfigMain: dict = configMain
            if dictConfigMain is None:
                sMsg = getResourceMsg("MSG:Config is not found by name {0}")
                raise MyException(sMsg.format(configName), EX_CONFIG_INVALID)
            return dictConfigMain
        except Exception as ex:
            raise MyException(getResourceMsg("MSG:Undefined config {0}:{1}:{"
                                             "2}").format(
                self.fileConfigName, self.mainkey, configName),
                EX_CONFIG_INVALID, ex)


class ToolApplyResult(OrderedDict):
    def __init__(self) -> None:
        super().__init__()
        self.update({'val_orddict': OrderedDict()})
        # self.val_orddict = OrderedDict()  # сформированные значения
        self.update({'fail_reason': OrderedDict()})
        # self.fail_reason = OrderedDict()  # описание ошибки
        self.update({'bComplete': False})
        # self.bComplete = False  # признак полностью сформированного значения
        self.update({'bChanged': False})
        # self.bChanged = False  # признак "улучшения значения"

    def getValues(self) -> OrderedDict:
        return self.get('val_orddict')

    def updateValues(self, values: dict):
        self.get('val_orddict').update(values)

    def getFailReason(self) -> OrderedDict:
        return self.get('fail_reason')

    def setFailReason(self, failReason):
        self.getFailReason().clear()
        if isinstance(failReason, dict):
            self.getFailReason().update(failReason)

    def isComplete(self) -> bool:
        return self.get('bComplete')

    def isChanged(self) -> bool:
        return self.get('bChanged')

    def setChanged(self, b: bool):
        self.update({'bChanged': b})

    def setComplete(self, b: bool):
        self.update({'bComplete': b})


# noinspection PyPep8Naming
class ToolConfigurable(abc.ABC):

    def __init__(self):
        self.sName = ''
        self.cfgDict = dict()

    def _initAsConfig(self, sName: str, **cfgDict):
        self.sName = sName
        self.cfgDict = dict(cfgDict)

    @classmethod
    @abc.abstractmethod
    def create_instance(cls):
        pass

    @classmethod
    def create_new_instance(cls, sName: str, **cfgDict):
        newObject: ToolConfigurable = cls.create_instance()
        newObject._initAsConfig(sName, **cfgDict)
        return newObject

    @classmethod
    def create_tool_instance(cls, sName: str, **cfgDict) -> object:
        # создать именованный экземпляр инструмента в соответствии с
        # конфигурацией
        if cfgDict is None:
            # если конфигурации нет - создать пустое чучело своего класса
            tool = cls.create_instance()
            tool.sName = sName
            return tool

        modulename = cfgDict.get(MODULE_ARG)
        if modulename is None:
            raise MyException(getResourceMsg("MSG:Config value is none {0}.{"
                                             "1}").format(sName,
                                                          MODULE_ARG),
                              EX_CONFIG_NONE)

        classname = cfgDict.get(CLASS_ARG)
        if classname is None:
            raise MyException(getResourceMsg("MSG:Config value is none {0}.{"
                                             "1}").format(sName,
                                                          CLASS_ARG),
                              EX_CONFIG_NONE)
        # Получить класс инструмента по имени
        toolClass = strName2Class(modulename, classname, cls)

        # Создать экземпляр и проинициализировать по имени иконфигурации
        tool = toolClass.create_new_instance(sName, **cfgDict)
        if not isinstance(tool, cls):
            # это не тот класс который ждали!
            raise MyException(
                getResourceMsg("MSG:Config item {0} is {1}. But {"
                               "2} is expected").format(sName,
                                                        tool,
                                                        cls.getClassTitle()),
                EX_CONFIG_INVALID)

        return tool

    @classmethod
    def getClassTitle(cls) -> str:
        # заголовок имени класса для сообщений
        return "" + cls.__module__ + "." + cls.__name__

    def getName(self) -> str:
        if self.sName is None:
            raise MyException(getResourceMsg("MSG:None Instance {0}").format(
                self.getClassTitle()), EX_TOOL_NONE)
        return self.sName

    def getCfg(self) -> dict:
        if self.cfgDict is None:
            raise MyException(getResourceMsg("MSG:None Instance {0}").format(
                self.getClassTitle()), EX_TOOL_NONE)
        return self.cfgDict


# noinspection PyPep8Naming
def readDataDict(cfgDict: dict, cfgKeyData) -> dict:
    data = dict()
    if cfgDict is None:
        return data
    try:
        dataCfg: dict = cfgDict.get(cfgKeyData)
        if DATA_FILE_NAME in dataCfg.keys():
            if DATA_FILE_KEY in dataCfg.keys():
                dataCfg = ToolJsonConfigReader(dataCfg.get(DATA_FILE_NAME),
                                               mainKey=dataCfg.get(
                                                   DATA_FILE_KEY)).readMainConfig()
            else:
                dataCfg = ToolJsonConfigReader(
                    dataCfg.get(DATA_FILE_NAME)).readMainConfig()

        # исходная конфигурация данных
        data.update({DATA_SRC_KEY: dataCfg})

        # таблицы данных
        df_keys : list = list()
        df_frames : list = list()

        dfCfg = dataCfg.get(DATA_SRC_FRAMES_KEY)
        if isinstance(dfCfg, dict):
            dfKeys = list(dfCfg.keys())
            for dfKey in dfKeys:
                cfg = dfCfg.get(dfKey)
                dataFrame: pd.DataFrame = readDataFrame(**cfg)
                df_keys.append(dfKey)
                df_frames.append(dataFrame)
        data.update({DATA_FRAMES_KEYS: df_keys, DATA_FRAMES_TABLES: df_frames})
        return data
    except MyException as ex:
        raise ex
    except Exception as ex:
        raise MyException("MSG:CANNOT_GET_DATA", EX_CONFIG_NO_DATA, ex)


# noinspection PyPep8Naming
def initTools(cfgDict: dict, cfgKeyTools, cfgKeyApplyList) -> OrderedDict:
    # формирование списка инструментов
    tools = OrderedDict()
    if (cfgDict is None) or (cfgDict.get(cfgKeyTools, None) is None):
        # список инструментов вообще не определен
        return tools
    try:
        toolsCfg: dict = cfgDict.get(cfgKeyTools)
        apply_list = toolsCfg.get(cfgKeyApplyList)
        if TOOLS_FILE_NAME in toolsCfg.keys():
            if TOOLS_FILE_KEY in toolsCfg.keys():
                toolsCfg = ToolJsonConfigReader(toolsCfg.get(TOOLS_FILE_NAME),
                                                mainKey=toolsCfg.get(
                                                    TOOLS_FILE_KEY)).readMainConfig()
            else:
                toolsCfg = ToolJsonConfigReader(toolsCfg.get(
                    TOOLS_FILE_NAME)).readMainConfig()

        if apply_list is None:
            # пусть работают как попало
            tools.update(toolsCfg)
        else:
            # работать только перечисленным и в указанном порядке
            for apply_name in apply_list:
                tool = toolsCfg.get(apply_name)
                if tool is None:
                    # конфигурации на этот инструмент нет
                    tool = ToolAppliedNone.create_named_instance(apply_name)
                tools.update({apply_name: tool})
        return tools
    except Exception as ex:
        raise MyException("MSG:CANNOT_GET_TOOLS", EX_CONFIG_NO_TOOLS, ex)


# noinspection PyPep8Naming
def makeExceptionText(ex: object, extb) -> str:
    if isinstance(ex, MyException):
        return getResourceMsg("MYEXCEPTION: {0} : {1}").format(ex, extb)
    elif isinstance(ex, Exception):
        return getResourceMsg("EXCEPTION: {0} : {1}").format(ex, extb)
    elif isinstance(ex, BaseException):
        return getResourceMsg("CRITICAL_ERROR: {0} : {1}").format(ex, extb)
    else:
        return ''


# noinspection PyPep8Naming
class ToolExeEnv(ToolConfigurable):
    def __init__(self):
        super().__init__()
        self.tools = OrderedDict()
        self.data = None
        self.result = OrderedDict()
        self.bOnExecute = False
        self.startTime = None
        self.exeTime = None

    @classmethod
    def create_instance(cls):
        return ToolExeEnv()

    def _initAsConfig(self, sName: str, **cfgDict):
        super()._initAsConfig(sName, **cfgDict)
        # создание инструментов
        # получение исходных данных
        # подготовка лоханки результата
        self.tools = initTools(self.cfgDict, CFG_KEY_TOOLS,
                               CFG_KEY_APPLY_LIST)
        self.data = readDataDict(self.cfgDict, CFG_KEY_DATA)
        self.result = OrderedDict()
        self.bOnExecute = False
        self.startTime = None
        self.exeTime = None

    def release(self):
        if self.tools is not None:
            tKeys = self.tools.keys()
            for tKey in tKeys:
                # noinspection PyBroadException
                try:
                    t = self.tools.get(tKey)
                    if isinstance(t, ToolApplied):
                        t.release()
                except Exception:
                    logger.warning("cannot release tool {0}".format(tKey),
                                   exc_info=True)
        if self.data is not None:
            dKeys = self.data.keys()
            for dKey in dKeys:
                # noinspection PyBroadException
                try:
                    d = self.data.get(dKey)
                    if d is not None:
                        d.release()
                except Exception:
                    logger.warning("cannot release data {0}".format(dKey),
                                   exc_info=True)
        self.bOnExecute = False

    def execute(self) -> dict:
        # собственно выполнить пока все не выполнится, (т.е результат не
        #   перестанет  улучшаться)

        # список инструментов, которые надо попробовать применить пока
        # список не пуст и пока есть улучшения
        # для элемента списка - получить инструмент
        #   - если ошибка - записать ошибку в лоханку под именем инструмента
        #   - иначе получить результат инструмента в данной среде
        #   - если результат пустой - исключить инструмент из
        #       обработки
        #  - если результат изменился -считать ЕСТЬ УЛУЧШЕНИЕ
        #  - если результат окончательный - записать его под именем инструмента
        #       в лоханку, инструмент исключить из дальнейшей обработки
        # применяемые инструменты могут изменять исходные данные и добавлять
        # в среду новые приеняемые инструменты
        bExeStarted = False
        nExeNumber = 0
        exeResult = OrderedDict()
        self.startExecute()
        try:
            bExeStarted = True
            completeList = list()

            applyTools: OrderedDict = self.getApplyTools()
            applyList: list = list(applyTools.keys())
            for completeName in completeList:
                while applyList.count(completeName) > 0:
                    applyList.remove(completeName)

            while len(applyList) > 0:
                bChanged = False
                nExeNumber = nExeNumber + 1
                # Для всех еще не отработавших полностью
                for applyName in applyList:
                    t = applyTools.get(applyName, None)
                    if t is None:
                        # нет такого инструмента
                        completeList.append(applyName)
                        continue

                    if isinstance(t, dict):
                        # Инструмент еще не был инициализирован
                        tool: ToolApplied = self.initTool(applyName, t)
                        self.tools.update(
                            {applyName: tool})
                        bChanged = True
                        continue

                    if isinstance(t, ToolApplied):
                        # Применимый инструмент
                        toolApplied: ToolApplied = t
                        toolResult = toolApplied.apply(self)
                        bChanged = bChanged or toolResult.isChanged()
                        self.updateToolResult(applyName, toolResult)
                        if toolResult.isComplete():
                            completeList.append(applyName)

                # инстременты могли понапихать в заказ еще инструментов
                # поэтому получаем список заново
                applyTools: OrderedDict = self.getApplyTools()
                applyList: list = list(applyTools.keys())
                # выкидываем уже все сказавших - их результаты уже записаны
                for completeName in completeList:
                    while applyList.count(completeName) > 0:
                        applyList.remove(completeName)

                if not bChanged:
                    # никто ничего сделать не может
                    # прекращаем обработку
                    break
            # прекратили итерации обработки
            s = self.getName() + '.resume'
            if len(applyList) > 0:
                exeResult.update({s: 'Impossible to complete'})
            else:
                exeResult.update({s: 'Complete'})

        except MyException as ex:
            logger.exception(ex, exc_info=True)
            s = self.getName() + '.resume'
            exeResult.update({s: makeExceptionText(ex, traceback.format_exc(
                100))})
        except Exception as ex:
            logger.exception(ex, exc_info=True)
            s = self.getName() + '.resume'
            exeResult.update({s: makeExceptionText(ex, traceback.format_exc(
                100))})
        except BaseException as ex:
            logger.exception(ex, exc_info=True)
            s = self.getName() + '.resume'
            exeResult.update({s: makeExceptionText(ex, traceback.format_exc(
                100))})
        finally:
            if bExeStarted:
                self.result.update(exeResult)
                res = self.getResultDict()
                self.stopExecute()
                return res
            s = self.getName() + '.resume'
            return OrderedDict({s: getResourceMsg("MSG_V_OCHERED!")})

    def getResultDict(self):
        return self.result.copy()

    def startExecute(self):
        if self.bOnExecute:
            raise MyException(getResourceMsg("MSG_V_OCHERED!"), EX_V_OCHERED)
        self.bOnExecute = True
        self.startTime = datetime.datetime.now()
        self.exeTime = None
        self.result = OrderedDict()
        if isinstance(self.data, dict):
            sData = self.data.get(DATA_SRC_KEY)
            if isinstance(sData, dict):
                sData = sData.copy()
            self.result.update({RESULT_SRC_DATA_KEY: sData})

    def stopExecute(self):
        if self.bOnExecute:
            self.bOnExecute = False
            self.exeTime = datetime.datetime.now() - self.startTime

    def getApplyTools(self):
        return OrderedDict(self.tools)

    def initTool(self, applyName, toolCfg) -> object:
        tool = ToolApplied.create_tool_instance(applyName, **toolCfg)
        if isinstance(tool, ToolApplied):
            return tool
        raise MyException(getResourceMsg("MSG_UNSUPPORTED_TOOL_INSTANCE {"
                                         "0}").format(tool), EX_CLASS)

    def updateToolResult(self, applyName, toolResult):
        self.result.update({applyName: toolResult})

    def getSrcDataValue(self, dataKey: str):
        if isinstance(self.data, dict):
            dataSrc = self.data.get(DATA_SRC_KEY, None)
            # требуемые данные ищем в исходном перечне
            if isinstance(dataSrc, dict):
                k: set = set(dataSrc.keys())
                if k.issuperset([dataKey]):
                    return dataSrc.get(dataKey)
        return None

    def getResultDataValue(self, resultName: str, datakeys: list):
        keys: tuple
        if isinstance(self.result, dict):
            keys = tuple(self.result.keys())
        else:
            raise WaitDataException(waitList=["Result"])

        if keys.count(resultName) < 1:
            raise WaitDataException(waitList=["Result", resultName])

        applyResult = self.result.get(resultName)
        if not isinstance(applyResult, ToolApplyResult):
            raise WaitDataException(waitList=["Result", resultName])

        dValue = applyResult.getValues()
        if (datakeys is None) or len(datakeys) < 1:
            # все значения результата
            return dValue
        else:
            noData: list = list()
            for dKey in datakeys:
                noData.append(dKey)
                if not isinstance(dValue, dict):
                    # не словарь - на выход
                    break
                keys = tuple(dValue.keys())
                if keys.count(dKey) < 1:
                    # нет такого ключа - на выход
                    break
                # значение найдено - если оно искомое - возврат
                dValue = dValue.get(dKey)
                if len(noData) == len(datakeys):
                    return dValue
            # цикл закончен, но значение не найдено
            noData.insert(0, resultName)
            noData.insert(0, "Result")
            raise WaitDataException(waitList=noData)
        pass


    def getDataFrameValue(self, dataFameName: str,
                          dfvalidator_lambda,
                          dfrowFilter_lambda,
                          dataColumns: list):
        dataFrame: pd.DataFrame
        dfValue = None
        if isinstance(self.data, dict) and len(dataFameName) > 0 :
            dfKeys = self.data.get(DATA_FRAMES_KEYS, None)
            if isinstance(dfKeys, list):
                i = dfKeys.index(dataFameName)
                if (i >= 0):
                    t: list = self.data.get(DATA_FRAMES_TABLES)
                    dataFrame = t[i]
                    dfValue = dataFrame
                else:
                    dataFrame = None
                    dfValue = None
            else:
                dataFrame = None
                dfValue = None
            df: pd.DataFrame = dataFrame
            if not (dfvalidator_lambda is None):
                df = dfvalidator_lambda(df)

            if not (dfrowFilter_lambda is None):
                df = dfrowFilter_lambda(df)

            if len(dataColumns) > 0:
                dfValue = df[dataColumns]

        return dfValue



def eqResultOrderedDicts(old_orddict, res_orddict):
    if old_orddict is None or len(old_orddict) == 0:
        return res_orddict is None or len(res_orddict) == 0
    old_keys = set(old_orddict.keys())
    res_keys = set(res_orddict.keys())
    if not (old_keys == res_keys):
        return True
    for k in res_keys:
        old = json.dumps(old_orddict.get(k), indent=2, ensure_ascii=False)
        res = json.dumps(res_orddict.get(k), indent=2, ensure_ascii=False)
        if not (old == res):
            return False
    return True


# noinspection PyPep8Naming
class ToolApplied(ToolConfigurable):
    # применяемый инструмент

    def __init__(self):
        super().__init__()

    def _initAsConfig(self, sName: str, **cfgDict):
        super()._initAsConfig(sName, **cfgDict)

    @classmethod
    def create_new_instance(cls, sName: str, **cfgDict) -> object:
        ta = cls.create_instance()
        ta._initAsConfig(sName=sName, **cfgDict)
        return ta

    def apply(self, env: ToolExeEnv) -> ToolApplyResult:
        # получить предыдущий результат
        old_result = env.result.get(self.getName())
        # сформировать новый результат
        result: ToolApplyResult = self.impl_apply(env)
        # проверить наличие изменений в значениях и возмлжной ошибке выполнения
        result.setChanged(not self.eqResults(old_result, result))
        return result

    def release(self):
        pass

    @abc.abstractmethod
    def impl_apply(self, env: ToolExeEnv) -> ToolApplyResult:
        pass

    def eqResults(self, old_result, result) -> bool:
        if not isinstance(result, ToolApplyResult):
            sError = "Unexpected type of result {0}. Expected {1}"
            raise TypeError(sError.format(type(result), ToolApplyResult))
        if not isinstance(old_result, ToolApplyResult):
            return False
        # old_result: ToolApplyResult = old_result
        # сравнение ошибки
        if not eqResultOrderedDicts(old_result.getFailReason(),
                                    result.getFailReason()):
            return False
        # сравнение значений
        if not self.eqResultValues(old_result.getValues(),
                                   result.getValues()):
            return False
        return True

    # noinspection PyMethodMayBeStatic
    def eqResultValues(self, old_orddict, res_orddict):
        return eqResultOrderedDicts(old_orddict, res_orddict)


class ToolAppliedNone(ToolApplied):
    def impl_apply(self, env: ToolExeEnv):
        result: ToolApplyResult = ToolApplyResult()
        result.b_complete = True
        result.clearValues()
        failed: OrderedDict = OrderedDict({'failed_code': -2000,
                                           'failed_msg': getResourceMsg(
                                               "MSG_TOOL_IS_NOT_DEFINED {"
                                               "0}").format(self.getName())})
        result.setFailReason(failed)
        return result

    @classmethod
    def create_instance(cls):
        return ToolAppliedNone()

    @classmethod
    def create_named_instance(cls, apply_name) -> ToolApplied:
        obj = cls.create_instance()
        obj.sName = apply_name
        return obj
