import logging
from typing import IO

import myutils
from myutils.my_def import MyArgsExe
from myutils.my_exceptions import MyException

TOOL_TITLE_ARG = 'toolTitle'
TOOL_OUT_FILE_ARG = 'out_file'

logger = logging.getLogger(__name__)



class EGESample(MyArgsExe):
    def __init__(self):
        MyArgsExe.__init__(self)
        self.title = ''
        self.outFile = None

    @classmethod
    def create_instance(cls, **args):
        instanceObject = EGESample()
        strTitle = args.get(TOOL_TITLE_ARG)
        if (strTitle is not None):
            instanceObject.title = strTitle
        strFileOut = args.get(TOOL_OUT_FILE_ARG)
        if (strFileOut is not None):
            instanceObject.outFile = strFileOut
        return instanceObject


    def release(self):
        pass

    def exe_args(self, **args):
        #smsg = "" + self.__module__ + "." + self.__class__.__name__ + ":" +
        # self.title
        #Инициализация переменных
        r0=r1=r2_max=r2_maxmax=-2000
        r_check = -2000
        nNeedItems = 2
        while True:
            sInput = input("Укажите элемент последовательности:")
            sInput = sInput.strip()
            if (sInput.lower() == 'exit'):
                print("Ну и не больно то и хотелось...")
                break
            if (sInput.lower() == 'no'):
                if (nNeedItems > 0):
                    print("Указывай!")
                    continue
            nInput = self.readInt(sInput, 1, 999)
            if (nInput < 0):
                continue

            if (nInput % 3 == 0):
                r0 = max(r0, nInput)
            elif nInput % 3 == 1:
                r1 = max(r1, nInput)
            elif nInput % 3 == 2:
               if (nInput > r2_maxmax):
                   r2_maxmax, r2_max = nInput, r2_maxmax
               elif nInput > r2_max:
                   r2_max = nInput

            if (self.outFile is not None):
                if (nNeedItems < 2):
                    with open(self.outFile, 'a', encoding='utf-8') as f:
                       f.write("," + sInput)
                else:
                    with open(self.outFile, 'w', encoding='utf-8') as \
                            self.writeFile:
                        f.write(sInput)

            if (nNeedItems > 0):
                nNeedItems = nNeedItems -1
            if (nNeedItems > 0):
                print("надо еще элементов! продолжай!")
                continue


            #максимальное число R - являющееся суммой 2х различных элементов
            # и при делении на 3 дающее остаток 1.
            nCheck = max(r0+r1, r2_maxmax + r2_max)
            if (nCheck < 0):
                nCheck = 1
            print("Контрольное значение {:d}".format(nCheck))
            r_check = nCheck

            nCheckInput = 0
            while nCheckInput < 1:
                strCheck = input("укажите контрольное значение!")
                nCheckInput = self.readInt(strCheck, 1, None)

            if (nCheckInput == nCheck):
                print("Угадали!!")
            else:
                print("Нет!!! не угадали!")
        print('ЧАО!!!')
        if (self.outFile is not None) and (nNeedItems < 2):
            with open(self.outFile, 'a', encoding='utf-8') as self.writeFile:
                f.write("({:d})".format(r_check))

        return r_check

    def title(self):
        return self.title

    def readInt(self, strValue, nMin, nMax):
        try :
            smsg = "Требуется целое число."
            if (nMin is not None):
                smsg = smsg + " {:d} <= N".format(nMin)
                if (nMax is not None):
                    smsg = smsg + " => {:d}".format(nMax)
            elif (nMax is not None):
                smsg = smsg + " N => {:d}".format(nMax)

            intValue = int(strValue)
            if (nMin is not None and intValue < nMin):
                raise MyException("Нарушена нижняя граница {:d}".format(
                    nMin), -400)
            if (nMax is not None and intValue > nMax):
                raise MyException(
                    "Нарушена верхняя граница {:d}".format(nMax), -400)
            return intValue
        except Exception as ex:
            print(ex)
            print(smsg.format(strValue))
            return -2000
