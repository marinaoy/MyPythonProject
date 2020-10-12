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

PERSON_INDICATOR_DEFAULT = "person"
first_med_test_INDICATOR_DEFAULT = "first_med_test"

logger = logging.getLogger(__name__)

AboutValue = namedtuple('AboutValue', 'what_b why_dict')

Bound = namedtuple('Bound', 'min_v max_v')

Money = namedtuple('Money', '{0} {1}'.format(SUM, CURRENCY))

class ApplyBound(Bound):
    def verify(self, value) -> AboutValue:
       if self.min_v is None:
           pass
       else:
           if (value is None) or (value < self.min_v):
               return AboutValue(False,
                                 {"borders violated":
                                   "{0} < {1}".format(value, self.min_v)})
       if self.max_v is None:
           pass
       else:
           if (value is None) or (value > self.max_v):
               return AboutValue(False,
                                 {"borders violated":
                                   "{0} > {1}".format(value, self.max_v)})
       return AboutValue(True, {})


class ApplyIndicator01(ToolApplied):
    # вычисляет значение возраста-пола в принятой данной группой
    # интикаторов форме

    def __init__(self):
        super().__init__()
        self.first_med_test = first_med_test_INDICATOR_DEFAULT

    def _initAsConfig(self, sName: str, **cfgDict):
        super()._initAsConfig(sName, **cfgDict)
        self.first_med_test = cfgDict.get(
            "med_test_indicator",
            first_med_test_INDICATOR_DEFAULT)

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


            vMedic01 = env.getResultDataValue(self.first_med_test,datakeys=["b_medical"])
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
        self.person_indicator = PERSON_INDICATOR_DEFAULT

    def _initAsConfig(self, sName: str, **cfgDict):
        super()._initAsConfig(sName, **cfgDict)
        self.person_indicator = cfgDict.get("person_indicator", PERSON_INDICATOR_DEFAULT)

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
            v = env.getResultDataValue(self.person_indicator, datakeys=[AGE_y])
            if v >= 65:
                about_v = AboutValue(False, {"about_age": "too old"})
            else:
                about_v = AboutValue(True, {})

            b_good = b_good & about_v.what_b
            result.updateValues(about_v.why_dict)

            # Тушка?
            v1 = env.getResultDataValue(self.person_indicator, datakeys=[WEIGHT_kg])
            v2 = env.getResultDataValue(self.person_indicator, datakeys=[HEIGHT_cm])
            v3 = env.getResultDataValue(self.person_indicator, datakeys=[SEX])
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
            v41 = env.getResultDataValue(self.person_indicator,
                                         datakeys=[MONEY, CURRENCY])
            if (v41 is None) or ("RUR" == v41):
                about_v = AboutValue(False, {"about_currency":
                                                 "it's not money {"
                                                 "0}".format(v41),
                                             "about_money":
                                                 "no money - no "
                                                 "medical care"})
            v42 = env.getResultDataValue(self.person_indicator,
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


class ApplyInterval(ToolApplied):
    def __init__(self):
        super().__init__()
        self.value_name = ''
        # src, res - исходные или результат
        self.value_source = ['src']
        self.value_bound = ApplyBound(None, None)

    def _initAsConfig(self, sName: str, **cfgDict):
        super()._initAsConfig(sName, **cfgDict)
        self.value_name = cfgDict.get("value_name",
                                   '')
        self.value_source = cfgDict.get("value_source",
                                   ['src'])
        min_v = None
        if ('min_v' in cfgDict.keys()):
            min_v = cfgDict.get('min_v')
            min_v = float(min_v)
        max_v = None
        if ('max_v' in cfgDict.keys()):
            max_v = cfgDict.get('max_v')
            max_v = float(max_v)

        self.value_bound = ApplyBound(min_v, max_v)

    @classmethod
    def create_instance(cls):
        return ApplyInterval()

    def impl_apply(self, env: ToolExeEnv) -> ToolApplyResult:
        # оценивает результаты person
        # не слишком ли пациент старый, толстый, нищий...
        # и решает стоит ли его лечить
        result = ToolApplyResult()
        about_v: AboutValue
        b_good = True
        try :
            v: object
            if 'src' == self.value_source[0]:
                v = env.getSrcDataValue(self.value_name)
            elif 'res' == self.value_source[0]:
                res_name = None
                vkey = list()
                i = 0
                while i < len(self.value_source):
                    if i > 0:
                        if i == 1:
                            res_name = self.value_source[i]
                        else:
                            vkey.append(self.value_source[i])
                    i=i+1
                vkey.append(self.value_name)
                v = env.getResultDataValue(res_name, vkey)
            else:
                raise MyException("Unknown value source {0}".format(
                    self.value_source), -200)

            v_float = float(v)
            about_v = self.value_bound.verify(v_float)
            b_good = b_good & about_v.what_b

            result.updateValues({"b_value": b_good})
            if b_good:
                result.updateValues({"Norma": v_float})
            else:
                result.updateValues({"Problem": v_float})
                result.updateValues(about_v.why_dict)
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





