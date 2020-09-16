import logging
import sys
import traceback

import myutils
from myutils import my_exceptions
from myutils.my_def import MyArgsExe
from myutils.my_exceptions import MyException

logger = logging.getLogger(__name__)

FILENAME_ARG = 'file'

class MyUnknown(MyArgsExe):
    def __init__(self):
        pass

    def create_instance(self, **args):
        return MyUnknown()

    def release(self):
        pass

    def exe_args(self, **args):
        raise MyException(stext="Я неизвестный науке зверь!", ncode=-300)


class MyFileSample(MyArgsExe):
    file = None

    def __init__(self):
        pass

    def create_instance(self, **args):
        return MyFileSample()

    def release(self):
        if self.file is None:
            pass
        else:
            myutils.my_utils.try_finally_io_close(f=self.file)
            self.file = None

    def exe_args(self, **args):
        if self.file is not None:
            raise MyException(stext="Некий файл уже в работе!", ncode=-101)
        if args is None:
            args = {}
        try:
            # считаем слова, логируем результат.
            filename = args.get(FILENAME_ARG)
            if filename is None:
                raise MyException(stext="не указано имя файла", ncode=-102)
            with open(filename, 'r+', encoding='utf-8') as self.file:
                file_data = self.file.read()
                words = file_data.split(" ")
                final_word_count: int = len(words)
                strinfo = 'Count = {:d} words'.format(final_word_count)
                logger.info(strinfo)
                self.file.write(strinfo)
                # print(strinfo)
                self.release()

                if final_word_count > 10:
                    # e0: Exception = Exception("WOW!")
                    # raise e0
                    raise my_exceptions.MyException(
                        stext='Очень много слов {:d}! Устай!'.format(
                            final_word_count),
                        ncode=-10)
                return final_word_count
        except my_exceptions.MyException as e:
            logger.exception(e, exc_info=True)
            return e.getcode()
        except OSError as e:
            logger.exception(e, exc_info=True)
            # print(e)
            # print(e.with_traceback())
            return -11
        except Exception as e:
            logger.error("Неопознанная ошибка: %s", traceback.format_exc())
            try:
                my = my_exceptions.MyException(
                    stext='что-то сдохло',
                    ncode=my_exceptions.MY_EXCEPTION_CODE_UNK,
                    exreason=e)
                raise my
            except Exception as mye:
                tb = sys.exc_info()[2]
                logger.exception(mye.with_traceback(tb))

            return False
        finally:
            self.release()

