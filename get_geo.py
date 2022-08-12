from loguru import logger as l

# from geopy import Nominatim # для преобразования координат в адрес
# from fake_useragent import UserAgent # для генерация рандомного юзерагента
# from pprint import pprint
#
# # генерируем рандомный юзерагент
# ua = UserAgent()
# random_user_agent = ua.random
#
# # получаем адрес, используя координаты и ранее созданный юзерагент
# coordinates = '43.3222965, 45.7258939'
# nominatim = Nominatim(user_agent = random_user_agent)
# location = nominatim.reverse(coordinates)
#
# pprint(location.raw)
#



# def get_number_product(string):
#     number = ""
#     i = string.split("шт")[0]
#     print(i)
#     for j in range(1, len(i)):
#         if i[-j].isdigit():
#             number += str(i[-j])
#         if i[-j].isalpha(): return number[::-1]
#     return number[::-1]
