

def convert_price(price):
    convert = ""
    def string_numbers_convert(string):
        flag = False
        for i in string:
            if i.isdigit():
                flag = True
        return flag
        
    for string in price.split(" "):
        if string_numbers_convert(string=string):
            for i in string:
                if i == "т" or i.isdigit():
                    convert += i.replace("т", "000")


    return int(str(convert) \
        .replace(".", "") \
            .replace(",", "") \
                .replace(";", "")
    )

print(convert_price("Итого с доставкой: 56000₽"))