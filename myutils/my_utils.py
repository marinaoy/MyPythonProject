from typing import IO
import logging

logger = logging.getLogger(__name__)


def try_finally_io_close(f: IO):
    try:
        if f is not None:
            fio: IO = f
            logger.info("try close {0}".format(fio.name))
            f.close()
            logger.info("closed {0}".format(fio.name))
        elif f is None:
            pass
        else:
            logger.warning('Not IO ')
    except BaseException as ex:
        logger.error(" cannot close {0} : {1}".format(f, ex))
        logger.error(ex, exc_info=True)


def release_obj(objexe):
    if objexe is not None:
        from myutils.my_def import MyArgsExe
        if isinstance(objexe, MyArgsExe):
            try:
                objexe.release()
            except Exception as ex:
                logger.error(" cannot release {0} : {1}".format(objexe, ex))
                logger.error(ex, exc_info=True)
            except BaseException as ex:
                logger.error(" cannot release {0} : {1}".format(objexe, ex))
                logger.error(ex, exc_info=True)
            finally:
                logger.info("Released {0}".format(objexe))
