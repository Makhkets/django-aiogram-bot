from django.db import models
import string
import random

def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


class Profile(models.Model):
    user_id = models.CharField(max_length=50, verbose_name="Айди пользователя")
    first_name = models.CharField(max_length=100, verbose_name="Имя", null=True, blank=True)
    username = models.CharField(max_length=50, verbose_name="Имя пользователя", default="Отсутствует username", null=True, blank=True)
    role = models.CharField(max_length=200, default="", verbose_name="Роль пользователя")

    def __str__(self):
        return str(self.first_name)

    class Meta:
        verbose_name = "Аккаунты"
        verbose_name_plural = "Аккаунты"

class Applications(models.Model):
    note = models.CharField(max_length=5000, verbose_name="Примечание")
    address = models.CharField(max_length=5000, verbose_name="Адрес")
    product = models.CharField(max_length=5000, verbose_name="Товар")
    price = models.CharField(max_length=100000, verbose_name="Цена")
    photo = models.ImageField(upload_to="images/%Y/%m/%d", verbose_name="Фото", blank=True, null=True)
    phone = models.CharField(max_length=100, verbose_name="Номер телефона")
    direction = models.CharField(max_length=400, verbose_name="Направление", null=True, blank=True)
    canceled_reason = models.CharField(max_length=3000, verbose_name="Причина отмены заказа", blank=True, null=True)
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name="Пользователь который добавил товар")
    create_time = models.DateTimeField(auto_now=True, verbose_name="Время создании заявки")
    driver = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name="Водитель который принял заказ", related_name="drive_user", null=True, blank=True)
    status = models.CharField(max_length=200, blank=True, null=True, default="Ожидание подтверждения", verbose_name="Статус товара")
    location = models.CharField(max_length=3000, verbose_name="Локация водителя", blank=True, null=True)
    time_update_location = models.DateTimeField(auto_now=True, verbose_name="Время изменения локации")

    def __str__(self):
        return str(self.product)

    class Meta:
        verbose_name = "Заявки"
        verbose_name_plural = "Заявки"

class RoleCode(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="create_user", verbose_name="Пользователь который создал код")
    active_user = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="active_user", blank=True, null=True, verbose_name="Пользоватлеь который активировал код")
    code = models.CharField(max_length=200, verbose_name="Код")
    role = models.CharField(max_length=200, verbose_name="Роль которая выдается после активация кода")
	
    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name = "Коды"
        verbose_name_plural = "Коды"

