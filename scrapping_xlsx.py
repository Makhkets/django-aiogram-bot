import re


def convert_price(price):
    convert = ""
    def string_numbers_convert(string):
        flag = [False, False]
        for i in string:
            if i.isdigit():
                flag[0] = True

        if flag[0]:
            for i in string:
                if i == "т":
                    flag[1] = True
        
        if flag[0] and flag[1]: return True
        return False
        
    for string in price.split(" "):
        if string_numbers_convert(string=string):
            convert += string.replace("т", "000")


    return int(str(convert) \
        .replace(".", "") \
            .replace(",", "") \
                .replace(";", "")
    )

print(convert_price("рублей 1т,"))