import pandas as pd

import logging

from myutils.my_exceptions import MyException

logger = logging.getLogger(__name__)

CFG_KEY_READER = 'data_reader'
CSV_READER = 'csv'
CFG_KEY_FILE = 'file_name'
CFG_KEY_CSV_DELIMITER = 'delimiter'
CFG_KEY_CSV_NAMES = 'names'


EX_UNKNOWN_READER = -401


def readDataCSV(**dataCfg) -> pd.DataFrame:
    fileName = dataCfg.get(CFG_KEY_FILE)
    delimiter = dataCfg.get(CFG_KEY_CSV_DELIMITER, ';')
    names = dataCfg.get(CFG_KEY_CSV_NAMES)
    dataFrame = pd.read_csv(fileName, delimiter=delimiter, names=names,
                            low_memory=True)
    return dataFrame


def readDataFrame(**dataCfg) -> pd.DataFrame:
    sReader = dataCfg.get(CFG_KEY_READER)
    if CSV_READER == sReader:
        return readDataCSV(**dataCfg)
    raise MyException("MSG_UNKNOWN_READER: {0} = {1}".format(CFG_KEY_READER,
                                                             sReader),
                      EX_UNKNOWN_READER)