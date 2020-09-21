import sys
import json
import logging.config
from typing import Dict, Any

import myutils.my_utils
import myutils.my_def
import myutils.my_exceptions

# logging.config.fileConfig('my_configs\\Mylogging.ini',
#                           disable_existing_loggers=False)
# logger = logging.getLogger(__name__)


with open("my_configs\\python_logging_configuration.json",
          'r') as logging_configuration_file:
    config_dict = json.load(logging_configuration_file)
logging.config.dictConfig(config_dict)
# Запись о том, что logger настроен
logger = logging.getLogger(__name__)
logger.info('Настройка логгирования окончена!')


#

objexe = None


if __name__ == '__main__':
    from myutils.my_configs import MyJsonConfigReader as MyConfigReader
    args = MyConfigReader().readArgs()
    nresult: int = -1
    try:
        factory = myutils.my_def.MyToolFactory()
        objexe = factory.create_obj_exe(**args)
        nresult = objexe.exe_args(**args)
    except myutils.my_exceptions.MyException as ex:
        nresult = ex.getcode()
        logger.exception(ex, exc_info=True)
    except Exception as ex:
        nresult = -10
        logger.exception(ex, exc_info=True)
    except BaseException as ex:
        nresult = -100
        logger.exception(ex, exc_info=True)
    finally:
        if objexe is not None:
            myutils.my_utils.release_obj(objexe)
        objexe = None
        if isinstance(nresult, int):
            logger.info("Result {:d}".format(nresult))
        else:
            logger.info("Result {}".format(nresult))
