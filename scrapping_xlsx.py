import re

def convert_phone_number(phone):
    dig = r'[\s-]*(\d)' * 6
    for i in re.findall(r'([78])[\s\(]*(\d{3})[\s\)]*(\d)' + dig, phone):
        res = ''.join(i)
        return res[0].replace("8", "7") + res[1:]

def convert_price(price):
    return int(str(price).lower() \
            .replace("-", "") \
            .replace(".", "") \
            .replace(",", "") \
            .replace("т", "000"))

