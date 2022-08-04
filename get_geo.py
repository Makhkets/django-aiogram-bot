from geopy import Nominatim # для преобразования координат в адрес
from fake_useragent import UserAgent # для генерация рандомного юзерагента
from pprint import pprint

# генерируем рандомный юзерагент
ua = UserAgent()
random_user_agent = ua.random

# получаем адрес, используя координаты и ранее созданный юзерагент
coordinates = '43.3222965, 45.7258939'
nominatim = Nominatim(user_agent = random_user_agent)
location = nominatim.reverse(coordinates)

pprint(location.raw)

