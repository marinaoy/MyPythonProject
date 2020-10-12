import sys
import json
import logging.config
import datetime

import myutils.my_utils
import myutils.my_def
import myutils.my_exceptions

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
    from myutils.my_tools import ToolJsonConfigReader as ToolConfigReader
    from myutils.my_tools import ToolExeEnv
    sExeConfigName = 'analyz'
    sExeConfigFile = "my_configs\\analyz_config.json"

    cfg = ToolConfigReader(sExeConfigFile, sExeConfigName).readMainConfig()
    nresult = None
    exe_env = None
    try:
        exe_env: ToolExeEnv = ToolExeEnv.create_new_instance(sExeConfigName, **cfg)

        result:dict = exe_env.execute()

        delta: datetime.timedelta = exe_env.exeTime
        logger.info("execute by {0} ".format(delta.total_seconds()))

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
        if exe_env is not None:
            myutils.my_utils.release_obj(exe_env)
        objexe = None
        if isinstance(nresult, int):
            logger.info("Result {:d}".format(nresult))
        else:
            try:
                sResult = json.dumps(result, indent=2, ensure_ascii=False)
                logger.info("Result {0}".format(result))
                logger.info("Result as json string {0}".format(sResult))
            except Exception as logEx:
                logger.warning("Exception on loggin result", exc_info=True)
