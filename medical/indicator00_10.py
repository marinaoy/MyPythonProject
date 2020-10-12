from collections import OrderedDict
from collections import namedtuple
import datetime

from myutils.my_exceptions import MyException
from myutils.my_tools import ToolApplied, ToolExeEnv, ToolApplyResult, \
    WaitDataException

import logging

FAIL_MSG = 'fail_msg'

FAIL_CODE = 'fail_code'

SUM = "SUM"

CURRENCY = "CURRENCY"

AGE_m = "AGE.m"

AGE_ym = "AGE.ym"

AGE_y = "AGE.y"

MONEY = "MONEY"

HEIGHT_cm = "HEIGHT.cm"

WEIGHT_kg = "WEIGHT.kg"

SEX = "SEX"

DATE_BIRTH = "DateBirth"
logger = logging.getLogger(__name__)

AboutValue = namedtuple('AboutValue', 'what_b why_dict')

Money = namedtuple('Money', '{0} {1}'.format(SUM, CURRENCY))

class ApplyIndicator01(ToolApplied):
    # вычисляет значение возраста-пола в принятой данной группой
    # интикаторов форме

    def __init__(self):
        super().__init__()

    @classmethod
    def create_instance(cls):
        return ApplyIndicator01()


    def impl_apply(self, env: ToolExeEnv) -> ToolApplyResult:
        result: ToolApplyResult = ToolApplyResult()
        data: OrderedDict = OrderedDict()
        try:
            dBirth = env.getSrcDataValue(DATE_BIRTH)
            dSex = env.getSrcDataValue(SEX)
            dWeight = env.getSrcDataValue(WEIGHT_kg)
            dHeight = env.getSrcDataValue(HEIGHT_cm)
            dMoney = env.getSrcDataValue(MONEY)
            data.update({SEX: dSex, DATE_BIRTH: dBirth, WEIGHT_kg: dWeight,
                         HEIGHT_cm: dHeight, MONEY: dMoney})
            if isinstance(dBirth, str):
                dBirth = datetime.date.fromisoformat(dBirth)
                data.update({DATE_BIRTH: dBirth.isoformat()})
            if isinstance(dBirth, datetime.date):
                dToday = datetime.date.today()
                age_year = dToday.year - dBirth.year + (dToday.month -
                                                        dBirth.month) / 12
                age_month = (dToday.month - dBirth.month) % 12
                data.update({AGE_y: age_year,
                             AGE_ym: age_month,
                             AGE_m: age_year * 12 + age_month})

            if isinstance(dSex, str):
                dSex = dSex.strip().upper()

            if dWeight is not None:
                dWeight = float(dWeight)

            if dHeight is not None:
                dHeight = float(dHeight)

            money = None
            if isinstance(dMoney, dict):
                c = dMoney.get(CURRENCY)
                m = float(dMoney.get(SUM))
                money = OrderedDict({CURRENCY:c, SUM:m})

            data.update({SEX: dSex, WEIGHT_kg: dWeight,
                         HEIGHT_cm: dHeight, MONEY: money})

            # Это был пример получения необходимого значения из данных
            # DataFrame
            # validator = lambda df: df
            # rowFilter = lambda df: df[df['y'].isin(['a','c'])&df[
            #     'x2']>0]
            # v = env.getDataFrameValue("dataFrame01", validator,
            #                           rowFilter,
            #                           ["y","x2"])
            # logger.debug(v)


            vMedic01 = env.getResultDataValue("medic01",datakeys=["b_medical"])
            if vMedic01 is None:
                 result.setComplete(False)
            else :
                result.updateValues({"Medicable": vMedic01})
                result.setComplete(True)

        except WaitDataException as ex:
            result.setComplete(False)
            result.setFailReason({"data_required": ex.getWaitList()})
            return result
        except MyException as ex:
            failReason = OrderedDict()
            failReason.update({FAIL_CODE: ex.getcode(),
                               FAIL_MSG: "{0}".format(ex)})
            result.setFailReason(failReason)
            logger.exception(ex, exc_info=True)
        except Exception as ex:
            failReason = OrderedDict()
            failReason.update({FAIL_CODE: -1100,
                               FAIL_MSG: "{0}".format(ex)})
            result.setFailReason(failReason)
            logger.exception(ex, exc_info=True)
        finally:
            result.updateValues(data)

        return result




class ApplyIndicator02(ToolApplied):
    def __init__(self):
        super().__init__()

    @classmethod
    def create_instance(cls):
        return ApplyIndicator02()

    def impl_apply(self, env: ToolExeEnv) -> ToolApplyResult:
        # оценивает результаты person
        # не слишком ли пациент старый, толстый, нищий...
        # и решает стоит ли его лечить
        result = ToolApplyResult()
        about_v: AboutValue
        b_good = True
        try :
            # Возраст?
            v = env.getResultDataValue("person", datakeys=[AGE_y])
            if v >= 65:
                about_v = AboutValue(False, {"about_age": "too old"})
            else:
                about_v = AboutValue(True, {})

            b_good = b_good & about_v.what_b
            result.updateValues(about_v.why_dict)

            # Тушка?
            v1 = env.getResultDataValue("person", datakeys=[WEIGHT_kg])
            v2 = env.getResultDataValue("person", datakeys=[HEIGHT_cm])
            v3 = env.getResultDataValue("person", datakeys=[SEX])
            if (not isinstance(v3, str) or len(v3) < 1):
                about_v = AboutValue(False, {"about_sex":
                                                 "unknown {0}".format(v3)})
            else:
                v3 = v3[0].upper()
                if v3 == "F":
                    if v2-110 < v1:
                        about_v = AboutValue(False, {"about_body": "too fat"})
                    else:
                        about_v = AboutValue(True, {})
                elif v3 == "M":
                    if v2 - 100 < v1:
                        about_v = AboutValue(False, {"about_body": "too fat"})
                    else:
                        about_v = AboutValue(True, {})
                else:
                    about_v = AboutValue(False, {"about_sex":
                                                     "unknown {0}".format(v3)})
            b_good = b_good & about_v.what_b
            result.updateValues(about_v.why_dict)

            # Деньги?
            v41 = env.getResultDataValue("person", datakeys=[MONEY, CURRENCY])
            if (v41 is None) or ("RUR" == v41):
                about_v = AboutValue(False, {"about_currency":
                                                 "it's not money {"
                                                 "0}".format(v41),
                                             "about_money":
                                                 "no money - no "
                                                 "medical care"})
            v42 = env.getResultDataValue("person",
                                         datakeys=[MONEY, SUM])
            if (v42 is None)or(v42 < 1000):
                about_v = AboutValue(False, {"about_money":
                "little money {0} {1} - no medical care".format(v42, v41)})
            else:
                about_v = AboutValue(True, {})
                pass

            b_good = b_good & about_v.what_b

            result.updateValues(about_v.why_dict)
            if b_good:
                result.updateValues({"about_medical_care": "Yes! Sure!!!)))",
                                     "b_medical": True})
            else:
                result.updateValues({"about_medical_care": "No! Hopeless(((",
                                     "b_medical": False})
            result.setComplete(True)
            return result

        except WaitDataException as ex:
            result.setComplete(False)
            result.setFailReason({"data_required": ex.getWaitList()})
            return result
        except Exception as ex:
            sReason = "On error {0}".format(ex)
            logger.exception(sReason, exc_info=True)
            result.setComplete(False)
            result.setFailReason({"Shit happens": sReason})
            return result






