from django.db import models
from loguru import logger

import string
import random

from script.functions import updateSheet, append_to_sheet, getCoordinate

def generate_random_string(length):
    letters = string.ascii_lowercase
    rand_string = ''.join(random.choice(letters) for i in range(length))
    return rand_string


class Profile(models.Model):
    CHOICES = (
        ("Роль не выдана", "Роль не выдана"),
        ("Упаковщик-Логист", "Упаковщик-Логист"),
        ("Снабженец", "Снабженец"),
        ("Админ", "Админ"),
        ("Менеджер", "Менеджер"),
        ("Логист", "Логист"),
        ("Оператор", "Оператор"),
        ("Водитель", "Водитель"),
        ("Упаковщик", "Упаковщик"),
    )

    user_id = models.CharField(max_length=50, verbose_name="Айди пользователя", null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name="Имя", null=True, blank=True, default="Неизвестно")
    username = models.CharField(max_length=50, verbose_name="Имя пользователя", null=True, blank=True, default="Отсутствует username")
    role = models.CharField(max_length=200, default="Роль не выдана", verbose_name="Роль пользователя", choices=CHOICES)

    def __str__(self):
        return str(self.first_name)

    class Meta:
        verbose_name = "Аккаунты"
        verbose_name_plural = "Аккаунты"



class Products(models.Model):
    product = models.CharField(max_length=1000, verbose_name="Товар")
    count = models.IntegerField(verbose_name="Количество")
    opt_price = models.PositiveIntegerField(verbose_name="Оптовая Цена")
    availability = models.BooleanField(default=True, verbose_name="Наличие")
    photo = models.CharField(max_length=3000, verbose_name="Фото", blank=True, null=True)
    product_suum = models.PositiveIntegerField(verbose_name="Сумма товара", blank=True, null=True) # автоматически
    product_percent = models.FloatField(verbose_name="2.5% От Суммы Товара", blank=True, null=True)     # автоматически
    fake_count = models.PositiveIntegerField(default=0)

    # product_percent = models.FloatField(verbose_name="2.5% От Общей Суммы")
    # total_amount = models.PositiveIntegerField(verbose_name="Общая сумма товара", blank=True, null=True) # автоматически
    # total_count = models.PositiveIntegerField(verbose_name="Общее количество")

    def __str__(self):
        return str(self.product)

    class Meta:
        verbose_name = "Товары"
        verbose_name_plural = "Товары"


class Applications(models.Model):
    CHOICES = (
        ("Ожидает отправки", "Ожидает отправки"),
        ("Неизвестный статус", "Неизвестный статус"),
        ("Передан логисту", "Передан логисту"),
        ("Передан диспетчеру", "Передан диспетчеру"),
        ("Фабричный брак", "Фабричный брак"),
        ("Дорожный брак", "Дорожный брак"),
        ("В дороге", "В дороге"),
        ("Ожидает упаковки", "Ожидает упаковки"),
        ("Упакован", "Упакован"),
        ("Ожидание подтверждения", "Ожидание подтверждения"),
        ("Отменен", "Отменен"),
        ("Доставлен", "Доставлен"),
    )


    note = models.CharField(max_length=5000, verbose_name="Примечание", null=True, blank=True)
    address = models.CharField(max_length=5000, verbose_name="Адрес", null=True, blank=True)
    product = models.CharField(max_length=5000, verbose_name="Товар", null=True, blank=True)
    price = models.CharField(max_length=100000, verbose_name="Цена", null=True, blank=True)
    phone = models.CharField(max_length=100, verbose_name="Номер", null=True, blank=True)
    checks_document = models.CharField(max_length=1000, verbose_name="Чек", blank=True, null=True)
    direction = models.CharField(max_length=400, verbose_name="Направление", null=True, blank=True)
    delivery_information = models.CharField(max_length=1000, verbose_name="Информация о доставке", blank=True, null=True)
    canceled_reason = models.CharField(max_length=3000, verbose_name="Причина отмены", blank=True, null=True)
    bool_status = models.BooleanField(verbose_name="Подт / Отм", null=True, blank=True)
    create_time = models.DateField(auto_now_add=True, verbose_name="Время создания")
    driver = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name="Водитель", related_name="drive_user", null=True, blank=True)
    status = models.CharField(max_length=200, blank=True, null=True, default="Ожидание подтверждения", verbose_name="Статус", choices=CHOICES)
    location = models.CharField(max_length=3000, verbose_name="Локация", blank=True, null=True)
    location_time = models.CharField(max_length=3000, verbose_name="Время локации", null=True, blank=True)
    time_update_location = models.DateTimeField(auto_now=True, verbose_name="Время изменения локации")
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name="Добавил", null=True, blank=True, default=1)
    products = models.ManyToManyField(Products, verbose_name="Привязанный товар", null=True, blank=True)
    bool_count = models.BooleanField(default=True, verbose_name="Хватает ли количество", null=True, blank=True)
    uniqueKey = models.CharField(max_length=5000, verbose_name="Уникальный идентификатор")

    def save(self, *args, **kwargs):
        # Если True, то не выполнять логику (if)
        super(Applications, self).save(*args, **kwargs)
        if kwargs.pop('perform_logic', False): pass
        else:
            logger.success("PERFORM LOGIC")
            if self.uniqueKey == "":
                # append_to_sheet(self)
                append_to_sheet(self)
                pass
            else:
                coordinate = getCoordinate(self.uniqueKey)
                updateSheet(coordinate, self)
            

    def save_alternative(self, *args, **kwargs):
        super(Applications, self).save(*args, **kwargs)
        

    @classmethod
    def create(cls, **kwargs):
        perform_logic = kwargs.pop('perform_logic', False)
        obj = cls(**kwargs)
        obj.save_alternative()
        if not perform_logic:
            append_to_sheet(obj)
        return obj


    def perform_logic(self):
        logger.success("Выполняется perform logic")
        coordinate = getCoordinate(self.uniqueKey)
        updateSheet(coordinate, self)


    class Meta:
        verbose_name = "Заявки"
        verbose_name_plural = "Заявки"



class RoleCode(models.Model):
    CHOICES = ( 
        ("Упаковщик-Логист", "Упаковщик-Логист"),
        ("Снабженец", "Снабженец"),
        ("Админ", "Админ"),
        ("Менеджер", "Менеджер"),
        ("Логист", "Логист"),
        ("Оператор", "Оператор"),
        ("Водитель", "Водитель"),
        ("Упаковщик", "Упаковщик"),
    )

    user = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="create_user", verbose_name="Пользователь который создал код")
    active_user = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="active_user", blank=True, null=True, verbose_name="Пользоватлеь который активировал код")
    code = models.CharField(max_length=200, verbose_name="Код")
    role = models.CharField(max_length=200, verbose_name="Роль которая выдается после активация кода", choices=CHOICES)
	
    def __str__(self):
        return str(self.code)

    class Meta:
        verbose_name = "Коды"
        verbose_name_plural = "Коды"
