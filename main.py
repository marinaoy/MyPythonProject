# TODO Тут будет город заложен
import Murzik
import my_exceptions
try:
    try:
        name = input("ты кто такой?")
        print("Брысь,-" + name + "-!!!")
        if name.__contains__("о"):
            print("буква о")
        elif name.__contains__("o") and name.__contains__("t"):
            print("не наша о")
        else:
            print("нету(((")

        chN = 'O' if name.__contains__("о") else 'щ'
        print(chN)
        for i in name:
            if i=='t':
                print("noooo!", end='\\'); print("t")
                print("if")
            else:
                print(i * 2, end='\\')
                print("else")
                raise my_exceptions.MyException("не нравится " + name)
    except BaseException as e:
        print("что-то сломалось...")
        print(e)
        print(e.__doc__)
        raise Exception(e)
    else:
        print("Обошлось")
    finally:
        print("НА ВЫХОД!")
except BaseException as e1:
    print(e1)
else:
    print("ok")
finally:
    print("finally")


