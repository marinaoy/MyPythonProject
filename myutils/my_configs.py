import json
import sys

import ijson as ijson

from myutils.my_exceptions import MyException
import logging

logger = logging.getLogger(__name__)

THIS_MODULE = 'my_configs'
MAIN_CONFIG_KEY = 'main_config'


class MyJsonConfigReader(object):
    def __init__(self):
        pass

    def readArgs(self):
        # exeModuleName = 'mysample.my_impl'
        # exeFactoryName = 'MyFileSample'
        # dictConfig = dict(toolFactoryModule=exeModuleName,
        #             toolFactoryClass = exeFactoryName,
        #             file='my_in\\myFile.txt')
        # to_json = {'myconfig': dictConfig,}

        fileConfigName = 'my_configs\\my_config.json'
        mainkey = "main_config"

        # чтение файла кусками - пример?
        # with open(fileConfigName, 'r', encoding='utf-8') as f:
        #      objects = ijson.items(f,prefix='')
        #      i = 0
        #      for row in objects:
        #          i = i + 1
        #          print("row {:d}".format(i))
        #          print(row)
        #      print("Все!")

        with open(fileConfigName, 'r', encoding='utf-8') as f:
           dictConfig = json.load(f)

        configName = dictConfig.get(MAIN_CONFIG_KEY)
        dictConfig0 = dictConfig.get(configName)

        # запись конфигурации в файл
        # iKey = 0
        # sKey = configName + iKey.__str__()
        # d = dict()
        # d.__setitem__(configName, dictConfig0)
        # iconfig = dictConfig.get(sKey)
        # while iconfig is not None:
        #     d.__setitem__(sKey, iconfig)
        #     iKey = iKey+1
        #     sKey = configName + iKey.__str__()
        #     iconfig = dictConfig.get(sKey)
        # d.__setitem__(sKey, dictConfig0)
        # #with open('my_out//my_config.json', 'a', encoding='utf-8') as fconfig:
        # with open(fileConfigName, 'w', encoding='utf-8') as fconfig:
        #     #fconfig.write(json.dumps(to_json))
        #     json.dump(d, fconfig, sort_keys=True, indent=2)

        return dictConfig0



if __name__ == "main":
    logger.info(THIS_MODULE + ' as main')
else:
    logger.info(THIS_MODULE + ' imported')