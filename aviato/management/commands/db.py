import re
import datetime

from aviato.models import *

from asgiref.sync import sync_to_async
from loguru import logger as l

def convert_phone_number(phone):
    dig = r'[\s-]*(\d)' * 6
    for i in re.findall(r'([78])[\s\(]*(\d{3})[\s\)]*(\d)' + dig, phone):
        res = ''.join(i)
        return res[0].replace("7", "8") + res[1:]

def convert_phone_number_to_seven(phone):
    dig = r'[\s-]*(\d)' * 6
    for i in re.findall(r'([78])[\s\(]*(\d{3})[\s\)]*(\d)' + dig, phone):
        res = ''.join(i)
        return res[0].replace("8", "7") + res[1:]

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

@sync_to_async
def get_user_or_create(user_id: str, username=None):
    try:
        return Profile.objects.get(user_id=user_id)
    except:
        return Profile.objects.create(
            user_id=user_id, role="Пользователь", username=username
        )


@sync_to_async
def get_all_ojid_check():
    return Applications.objects.filter(status="Доставлен", checks_document=None)


@sync_to_async
def get_all_users():
    return Profile.objects.all()


@sync_to_async
def create_code_employees(user_id, code, role):
    user = Profile.objects.get(user_id=str(user_id))
    return RoleCode.objects.create(user=user, code=code, role=role)


@sync_to_async
def get_user_or_error(user_id):
    try:
        return Profile.objects.get(user_id=str(user_id))
    except:
        return "Error"


@sync_to_async
def change_role_user(user_id, role):
    try:
        p = Profile.objects.get(user_id=user_id)
        p.role = role
        p.save()
        return p
    except:
        return "Error"


@sync_to_async
def find_code_and_apply(user_id, code):
    try:
        u = Profile.objects.get(user_id=str(user_id))
        c = RoleCode.objects.get(code=code)

        u.role = c.role
        c.active_user = u

        c.save()
        u.save()
        return u
    except:
        return "❌ Код не найден"


@sync_to_async
def product_edit(data, product_id):
    try:
        data = data.split("\n")

        product = data[0].replace("нет", "").replace("Нет", "")
        address = data[1].replace("нет", "").replace("Нет", "")
        phone = data[2].replace("нет", "").replace("Нет", "")
        price = data[3].replace("нет", "").replace("Нет", "")
        note = data[4].replace("нет", "").replace("Нет", "")


        a = Applications.objects.get(pk=product_id)
        a.note = note
        a.address = address
        a.product = product
        a.phone = convert_phone_number_to_seven(phone)
        a.price = convert_price(price)
        a.save()

        return "✅ Товар успешно изменен"
    except Exception as ex:
        return f"❌ Ошибка при загрузке товара ({ex})"


# @sync_to_async
# def get_products_inline(product):
#     p = Products.objects.filter(count__lt=1, availability=True)
#     for i in p:
#         i.availability = False
#         i.save()
#
#     product = product.lower()
#     return Products.objects.filter(product__contains=product, count__gte=1)


def get_product_count(string):
    pass

def get_number_product_1(string):
    try:
        number = ""
        if len(string) == 0: return "❌ Уберите лишний пробел в строке <b>'Товар'</b> "
        else:
            string = string.lower()
            i = string.split("шт")[0]
            for j in range(1, len(i)):
                if i[-j].isdigit():
                    number += str(i[-j])
                if i[-j].isalpha():

                    replace_text = f"{number[::-1]}шт"
                    orig_product = string.replace(replace_text, "").lower()
                    pr = Products.objects.get(product=orig_product)
                    if number:
                        pr.count -= int(number[::-1])
                    else: pr.count -= 1
                    pr.save()
                    return pr

            replace_text = f"{number[::-1]}шт"
            orig_product = string.replace(replace_text, "").lower()
            pr = Products.objects.get(product=orig_product)
            if number:
                pr.count -= int(number[::-1])
            else: pr.count -= 1
            pr.save()
            return pr
    except Exception as ex:
        return f"Такой товар не найден ({string}) ({str(ex)})"


@sync_to_async
def product_save(user_id, data):
    # try:
    user = Profile.objects.get(user_id=str(user_id))
    product = data[0]

    product = product.split(" ")
    PRODUCTS = []
    for prd in product:
        PRODUCTS.append(get_number_product_1(prd))
    for j in PRODUCTS:
        try:
            if "не найден" in j:
                return j
            elif "❌" in j:
                return j
        except:
            pass

    address = data[1].replace("нет", "").replace("Нет", "")
    phone = data[2].replace("нет", "").replace("Нет", "")
    price = data[3].replace("нет", "").replace("Нет", "")
    note = data[4].replace("нет", "").replace("Нет", "")

    a = Applications.objects.create(
        note=note,
        address=address,
        product=product,
        phone=convert_phone_number_to_seven(phone),
        price=convert_price(price),
        user=user,
        status="Ожидание подтверждения",
    )
    for i in PRODUCTS:
 
        if i.count < 0:
            a.bool_count = False

    a.products.set(PRODUCTS)
    a.save()

    return "✅ Успешно добавил заявку в базу"


# except Exception as ex: return f"❌ Ошибка при загрузке товара ({ex})"


@sync_to_async
def get_products():
    return Applications.objects.all()


@sync_to_async
def get_confirm_products():
    return Applications.objects.filter(status="Ожидание подтверждения")


@sync_to_async
def get_confirmed_products():
    return Applications.objects.filter(status="Упакован")


@sync_to_async
def get_pack_products():
    return Applications.objects.filter(status="Ожидает упаковки")

@sync_to_async
def pack_to_drive():
    return Applications.objects.filter(status="В дороге")


@sync_to_async
def pack_to_logist():
    return Applications.objects.filter(status="Передан диспетчеру")

@sync_to_async
def delete_product(product_id):
    try:
        a = Applications.objects.get(pk=product_id)
        a.status = "Отменен"
        a.bool_status = False
        a.save()
        return "✅ Товар успешно отменен"
    except Exception as ex:
        l.error(ex)
        return f"❌ Товар не был удален ({ex})"


@sync_to_async
def product_pack_conf(product_id):
    try:
        a = Applications.objects.get(pk=product_id)
        a.status = "Передан диспетчеру"
        a.save()
        return "✅ Товар передан диспетчеру"
    except Exception as ex:
        return "❌ " + str(ex)


@sync_to_async
def product_pack_logist(product_id):
    try:
        a = Applications.objects.get(pk=product_id)
        a.status = "Упакован"
        a.save()
        return "✅ Товар упакован и передан Логисту"
    except Exception as ex:
        return "❌ " + str(ex)

@sync_to_async
def report_info():
    try:
        expectation = Applications.objects.filter(
            status="Ожидание подтверждения"
        ).count()
        confirmed = Applications.objects.filter(status="Ожидает упаковки").count()
        canceled = Applications.objects.filter(status="Отменен").count()
        transferred = Applications.objects.filter(status="Ожидает отправки").count()
        y_logist = Applications.objects.filter(status="Упакован").count()
        transferred_dispatcher = Applications.objects.filter(status="Передан диспетчеру").count()
        drive = Applications.objects.filter(status="В дороге").count()
        delivered = Applications.objects.filter(status="Доставлен").count()
        matchs = Applications.objects.filter(status="Фабричный брак").count()
        matchs2 = Applications.objects.filter(status="Дорожный брак").count()
        product_ended = Products.objects.filter(count=0).count()

        text = f"""
Ожидающие подтверждения:  <b>{expectation}</b>
Ожидает упаковки:  <b>{confirmed}</b>
Отмененные:  <b>{canceled}</b>
Ожидает отправки:  <b>{transferred}</b>
Передано логисту: <b>{y_logist}</b>
Переданно диспетчеру:  <b>{transferred_dispatcher}</b>
В дороге:  <b>{drive}</b>
Дорожный брак: <b>{matchs2}</b>
Фабричный брак: <b>{matchs}</b>
Ожидающие товара: <b>{product_ended}</b>
Нет в наличии (Товары): <b>{Applications.objects.filter(bool_count=False).count()}</b>
Доставлено:  <b>{delivered}</b>
        """

        return text
    except Exception as ex:
        return "❌ " + str(ex)


@sync_to_async
def confirm_product(product_id):
    try:
        p = Applications.objects.get(pk=product_id)
        p.status = "Ожидает упаковки"
        p.bool_status = True
        p.save()
        return f"✅ Заказ <b>№{p.pk}</b> Ожидает упаковки"
    except Exception as ex:
        return "❌ " + str(ex)


@sync_to_async
def product_pack(product_id, dist):
    try:
        p = Applications.objects.get(pk=product_id)
        p.status = "Ожидает отправки"
        p.direction = dist
        p.save()
        return f"✅ Товар <b>№{p.pk}</b> ожидает отправки"
    except Exception as ex:
        return "❌ " + str(ex)


@sync_to_async
def handover_product_to_drive(product_id, user_id):
    try:
        u = Profile.objects.get(user_id=user_id)
        p = Applications.objects.get(pk=product_id)
        p.status = "В дороге"
        p.driver = u
        p.save()
        return "✅ Заказ успешно принят"
    except Exception as ex:
        "❌ " + str(ex)


@sync_to_async
def get_active_requests_drive(user_id):
    u = Profile.objects.get(user_id=str(user_id))
    return Applications.objects.filter(status="В дороге", driver=u)


@sync_to_async
def delivered(product_id):
    try:
        p = Applications.objects.get(pk=product_id)
        p.status = "Доставлен"
        p.save()
        return "✅ Заказ успешно доставлен"
    except Exception as ex:
        "❌ " + str(ex)


@sync_to_async
def change_location(user_id, location):
    try:
        u = Profile.objects.get(user_id=user_id)
        p = Applications.objects.filter(status="В дороге", driver=u)

        for _ in p:
            try:
                if location in _.location:
                    pass
                else:
                    if _.location is None:
                        _.location = location
                        _.location_time = str(datetime.datetime.now())
                        _.save()
                    else:
                        _.location += f" | {location}"
                        _.location_time += f" | {str(datetime.datetime.now())}"
                        _.save()
            except:
                _.location = location
                _.location_time = str(datetime.datetime.now())
                _.save()

        return "✅ Успешно"
    except Exception as ex:
        return "❌ " + str(ex)


@sync_to_async
def applications_drivers():
    try:
        return Applications.objects.filter(status="В дороге")
    except:
        pass


@sync_to_async
def plea_location(product_id):
    return Applications.objects.get(pk=product_id)


@sync_to_async
def admins_list():
    return Profile.objects.filter(role="Админ")


@sync_to_async
def find_product(product_id):
    return Applications.objects.get(pk=product_id)


@sync_to_async
def change_name(user_id, name):
    u = Profile.objects.get(user_id=user_id)
    u.first_name = name
    u.save()


@sync_to_async
def get_all_drivers():
    return Profile.objects.filter(role="Водитель")


@sync_to_async
def get_all_packers():
    return Profile.objects.filter(role="Упаковщик")


@sync_to_async
def get_product(product_id):
    return Applications.objects.get(pk=product_id)


@sync_to_async
def get_user(user_id):
    return Profile.objects.get(pk=user_id)


@sync_to_async
def get_user_userId(user_id):
    return Profile.objects.get(user_id=user_id)


@sync_to_async
def driver_confrimed(user, product):
    product.driver = user
    product.status = "В дороге"
    product.save()
    return product


@sync_to_async
def product_match(title, price, title2, price2, product_id, status):
    # try:
        p = Applications.objects.get(pk=product_id)
        p.status = status
        p.product = title2
        p.price = convert_price(price2)
        p.save()
        #
        Applications.objects.create(
            note=p.note,
            address=p.address,
            product=title,
            phone=p.phone,
            price=convert_price(price),
            user=p.user,
            bool_status=True,
            status="Ожидает отправки",
        )
        Applications.objects.create(
            note=p.note,
            address=p.address,
            product=title2,
            phone=p.phone,
            price=convert_price(price2),
            user=p.user,
            status="Доставлен",
        )
        

        return "✅ Успешно"
    # except Exception as ex:
    #     return "❌ " + str(ex) + "((()))"


@sync_to_async
def drive_products():
    return Applications.objects.filter(status="В дороге")


@sync_to_async
def get_operators():
    return Profile.objects.filter(role="Оператор")


@sync_to_async
def get_logists():
    return Profile.objects.filter(role="Логист")


@sync_to_async
def find_products(info):
    try:
        p = Applications.objects.filter(pk=info)
        if len(p) >= 1:
            return p

        if len(info) < 5:
            return None
        else:
            p = Applications.objects.filter(phone__contains=convert_phone_number_to_seven(info))
            if len(p) >= 1:
                return p

        return None
    except:
        return None


@sync_to_async
def get_money():
    a = Applications.objects.all()
    confirmed_request = Applications.objects.filter(status="Ожидает упаковки")
    dispatcher = Applications.objects.filter(status="Передан диспетчеру")
    packer = Applications.objects.filter(status="Ожидает отправки")
    driver = Applications.objects.filter(status="В дороге")

    total = 0
    total_driver = 0
    total_packer = 0
    total_confirmed = 0
    total_dispatcher = 0
    total_disp_pack_driv = 0

    total_sum_p = 0
    for i in Products.objects.all():
        total_sum_p += i.opt_price

    for dr in driver:
        try:
            total_disp_pack_driv += int(dr.price)
            total_driver += int(dr.price)
        except:
            pass

    for p in packer:
        try:
            total_disp_pack_driv += int(p.price)
            total_packer += int(p.price)
        except:
            pass

    for d in dispatcher:
        try:
            total_disp_pack_driv += int(d.price)
            total_dispatcher += int(d.price)
        except:
            pass

    for i in confirmed_request:
        try:
            total_confirmed += int(i.price)
        except:
            pass

    for i in a:
        try:
            if (
                i.status == "Отменен"
                or i.status == "Фабричный брак"
                or i.status == "Дорожный брак"
            ):
                pass
            else:
                total += int(i.price)
        except:
            pass

    text = f"""
<b>📋 Заявки:</b>
Итого 2,5% - <b>{round(total / 100 * 2.5, 10)} Рублей</b>
Объем, ₽ (Ожидает упаковки) - <b>{round(total, 10)} Рублей</b>
Общий объем диспетчера, упаковщика, водителя ₽ - <b>{round(total_disp_pack_driv, 10)} Рублей</b>
Объем у диспетчера, ₽ - <b>{round(total_dispatcher, 10)} Рублей</b>
Объем у упаковщика, ₽ - <b>{round(total_packer, 10)} Рублей</b>
Объем в дороге, ₽ - <b>{round(total_driver, 10)} Рублей</b> 

<b>🛒 Товары:</b>
Общая сумма Товаров: <b>{total_sum_p} Рублей</b>
2.5% От Общей Суммы:  <b> {(total_sum_p / 100) * 2.5} Рублей</b>
Общее количество Товаров: <b>{Products.objects.all().count()}</b>
    """
    return text


@sync_to_async
def set_dop_information(text, product_id):
    try:
        product = Applications.objects.get(pk=product_id)
        product.delivery_information = text
        product.save()
        return "✅ Успешно"
    except Exception as ex:
        return "❌ Ошибка (" + str(ex) + ")"


@sync_to_async
def set_path_file(product_id, path):
    p = Applications.objects.get(pk=product_id)
    p.checks_document = path
    p.save()


@sync_to_async
def get_ojid_confirmed():
    return Applications.objects.filter(status="Ожидание подтверждения")


@sync_to_async
def get_confirmed():
    return Applications.objects.filter(status="Ожидает упаковки")


@sync_to_async
def get_canceled():
    return Applications.objects.filter(status="Отменен")


@sync_to_async
def get_packers():
    return Applications.objects.filter(status="Ожидает отправки")


@sync_to_async
def get_dispatchers():
    return Applications.objects.filter(status="Передан диспетчеру")


@sync_to_async
def get_drive_pr():
    return Applications.objects.filter(status="В дороге")


@sync_to_async
def dorozh_brak_products():
    return Applications.objects.filter(status="Дорожный брак")


@sync_to_async
def fabr_brack_products():
    return Applications.objects.filter(status="Фабричный брак")


@sync_to_async
def oj_delivered():
    return Applications.objects.filter(status="Доставлен")


@sync_to_async
def oj_pr():
    return Products.objects.filter(count=0)


def get_number_product(string):
    number = ""
    i = string.split("шт")[0]
    print(i)
    for j in range(1, len(i)):
        if i[-j].isdigit():
            number += str(i[-j])
        if i[-j].isalpha():
            return number[::-1]
    return number[::-1]

@sync_to_async
def net_v_nalichii_logist():
    return Applications.objects.filter(status="Упакован")

@sync_to_async
def net_v_nalichii():
    return Applications.objects.filter(bool_count=False).exclude(status="Отменен").exclude(status="Доставлен")

@sync_to_async
def add_product_to_db(data):
    try:
        data = data.split("\n")

        product = data[0]
        count = data[1]
        price = data[2]
        photo = data[3]
        P = None
        if str(photo) == "-":
            P = Products.objects.create(
                product=product,
                count=count,
                opt_price=convert_price(price),
            )

        elif "http" in str(photo):
            P = Products.objects.create(
                product=product,
                count=count,
                opt_price=convert_price(price),
                photo=photo
            )

        else: return "❌ Неправильно ведена ссылка на фото (если оно отсутствует введите прочерк ( - ) без скобок )"
        P.product_suum = int(convert_price(price)) * int(count)
        P.fake_count = count
        P.product_percent = (int(convert_price(price)) * int(count)) / 100 * 2.5
        P.save()
        return "✅ Успешно добавлен товар"
    except Exception as ex: return f"❌ Ошибка {str(ex)}"


@sync_to_async
def find_products_tovar(number):
    try:
        return Products.objects.get(pk=number)
    except: pass
    
    try:
        return Products.objects.get(pk=number)
    except: pass

    return False

@sync_to_async
def change_product_tv(product_id, product_product):
    p = Products.objects.get(pk=product_id)
    p.product = product_product
    p.save()
    return "✅ Успешно"

@sync_to_async
def change_price_tv(product_id, new_count):
    p = Products.objects.get(pk=product_id)
    p.count += int(new_count)
    p.save()
    return "✅ Успешно"

@sync_to_async
def сhange_opt(product_id, price):
    p = Products.objects.get(pk=product_id)
    p.opt_price = convert_price(price)
    p.save()
    return "✅ Успешно"

@sync_to_async
def change_product_request(product_id, new_products):
    p = Applications.objects.get(pk=product_id)
    product = new_products
    product = product.split(" ")
    PRODUCTS = []
    for prd in product:
        PRODUCTS.append(get_number_product_1(prd))
    for j in PRODUCTS:
        try:
            if "не найден" in j:
                return j
        except:
            pass

    p.product = new_products.split(" ")
    p.save()
    return "✅ Успешно изменил товары!"

@sync_to_async
def change_address(product_id, new_address):
    p = Applications.objects.get(pk=product_id)
    p.address = new_address
    p.save()

    return "✅ Успешно"

@sync_to_async
def change_note(product_id, new_note):
    p = Applications.objects.get(pk=product_id)
    p.note = new_note
    p.save()

    return "✅ Успешно"


@sync_to_async
def change_price(product_id, new_price):
    p = Applications.objects.get(pk=product_id)
    p.price = convert_price(new_price)
    p.save()
    return "✅ Успешно"

@sync_to_async
def change_phone(product_id, new_phone):
    p = Applications.objects.get(pk=product_id)
    p.phone = convert_phone_number(new_phone)
    p.save()

    return "✅ Успешно"



@sync_to_async
def product_save_bez(user_id, data):
    try:
        user = Profile.objects.get(user_id=str(user_id))

        product = data[0].replace("нет", "").replace("Нет", "")
        address = data[1].replace("нет", "").replace("Нет", "")
        phone = data[2].replace("нет", "").replace("Нет", "").replace("-", "")
        price = data[3].replace("нет", "").replace("Нет", "")
        note = data[4].replace("нет", "").replace("Нет", "")

        a = Applications.objects.create(
            product=product,
            note=note,
            address=address,
            phone=convert_phone_number_to_seven(phone),
            price=convert_price(price),
            user=user,
            bool_count=None,
            status="Ожидание подтверждения",
        )

        a.save()

        return "✅ Успешно добавил заявку в базу"
    except Exception as ex: return f"❌ Произошла ошибка ({str(ex)})" 