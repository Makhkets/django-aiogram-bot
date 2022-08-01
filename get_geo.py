from geopy import Nominatim # для преобразования координат в адрес
from fake_useragent import UserAgent # для генерация рандомного юзерагента


# генерируем рандомный юзерагент
ua = UserAgent()
random_user_agent = ua.random

# получаем адрес, используя координаты и ранее созданный юзерагент
coordinates = '55.879699, 37.539002'
nominatim = Nominatim(user_agent = random_user_agent)
location = nominatim.reverse(coordinates)

print(location)