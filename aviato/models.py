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
        ("Подтвержден", "Подтвержден"),
        ("Отменен", "Отменен"),
        ("Передан упаковщику", "Передан упаковщику"),
        ("Передан логисту", "Передан логисту"),
        ("Упакован", "Упакован"),
        ("Доставлен", "Доставлен"),
        ("Фабричный брак", "Фабричный брак"),
        ("Дорожный брак", "Дорожный брак"),
        ("Ожидание подтверждения", "Ожидание подтверждения"),
        ("В дороге", "В дороге")
    )

    note = models.CharField(max_length=5000, verbose_name="Примечание")
    address = models.CharField(max_length=5000, verbose_name="Адрес")
    product = models.CharField(max_length=5000, verbose_name="Товар", null=True, blank=True)
    price = models.CharField(max_length=100000, verbose_name="Цена")
    phone = models.CharField(max_length=100, verbose_name="Номер")
    checks_document = models.CharField(max_length=1000, verbose_name="Чек", blank=True, null=True)
    direction = models.CharField(max_length=400, verbose_name="Направление", null=True, blank=True)
    delivery_information = models.CharField(max_length=1000, verbose_name="Информация о доставке", blank=True, null=True)
    canceled_reason = models.CharField(max_length=3000, verbose_name="Причина отмены", blank=True, null=True)
    bool_status = models.BooleanField(verbose_name="Подт / Отм", null=True, blank=True)
    create_time = models.DateField(auto_now=True, verbose_name="Время создания")
    driver = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name="Водитель", related_name="drive_user", null=True, blank=True)
    status = models.CharField(max_length=200, blank=True, null=True, default="Ожидание подтверждения", verbose_name="Статус", choices=CHOICES)
    location = models.CharField(max_length=3000, verbose_name="Локация", blank=True, null=True)
    location_time = models.CharField(max_length=3000, verbose_name="Время локации", null=True, blank=True)
    time_update_location = models.DateTimeField(auto_now=True, verbose_name="Время изменения локации")
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, verbose_name="Добавил")
    products = models.ManyToManyField(Products, verbose_name="Привязанный товар", null=True, blank=True)
    bool_count = models.BooleanField(default=True, verbose_name="Хватает ли количество", null=True, blank=True)

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

