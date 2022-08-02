
from asgiref.sync import sync_to_async
from loguru import logger as l

from aviato.models import *


@sync_to_async
def get_user_or_create(user_id: str, username=None):
    try:
        return Profile.objects.get(user_id=user_id)
    except:
        return Profile.objects.create(user_id=user_id, role="Пользователь",
                                      username=username)

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
    except: return "Error"

@sync_to_async
def change_role_user(user_id, role):
    try:
        p = Profile.objects.get(user_id=user_id)
        p.role = role
        p.save()
        return p
    except: return "Error"

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
    except: return "❌ Код не найден"

@sync_to_async
def product_edit(data, product_id):
    try:
        data = data.split("\n")
        note = data[0].replace("нет", "").replace("Нет", "")
        address = data[1].replace("нет", "").replace("Нет", "")
        product = data[2].replace("нет", "").replace("Нет", "")
        price = data[3].replace("нет", "").replace("Нет", "")
        phone = data[4].replace("нет", "").replace("Нет", "")
        photo = ""

        if data[5] == "нет" or data[5] == "Нет":
            pass
        else:
            photo = data[5]

        a = Applications.objects.get(pk=product_id)
        a.note = note
        a.address = address
        a.product = product
        a.phone = phone
        a.price = price
        photo=photo
        a.save()

        return "✅ Товар успешно изменен"
    except Exception as ex: return f"❌ Ошибка при загрузке товара ({ex})"


@sync_to_async
def product_save(user_id, data):
    try:
        user = Profile.objects.get(user_id=str(user_id))

        note = data[0].replace("нет", "").replace("Нет", "")
        product = data[1].replace("нет", "").replace("Нет", "")
        address = data[2].replace("нет", "").replace("Нет", "")
        phone = data[3].replace("нет", "").replace("Нет", "")
        price = data[4].replace("нет", "").replace("Нет", "")
        photo = ""
        if data[5] == "нет" or data[5] == "Нет":
            pass
        else:
            photo = data[5]

        Applications.objects.create(
            note=note,
            address=address,
            product=product,
            phone=phone,
            price=price,
            photo=photo,
            user=user,
            status="Ожидание подтверждения"
        )

        return "✅ Успешно добавил товар в базу"
    except Exception as ex: return f"❌ Ошибка при загрузке товара ({ex})"

@sync_to_async
def get_products():
    return Applications.objects.all()

@sync_to_async
def get_confirm_products():
    return Applications.objects.filter(status="Ожидание подтверждения")

@sync_to_async
def get_confirmed_products():
    return Applications.objects.filter(status="Подтвержден")

@sync_to_async
def get_pack_products():
    return Applications.objects.filter(status="Передан упаковщику")

@sync_to_async
def pack_to_drive():
    return Applications.objects.filter(status="")

@sync_to_async
def pack_to_logist():
    return Applications.objects.filter(status="Упакован")

@sync_to_async
def delete_product(product_id):
    try:
        a = Applications.objects.get(pk=product_id)
        a.status = "Отменен"
        a.save()
        return "✅ Товар успешно отменен"
    except Exception as ex: 
        l.error(ex)
        return f"❌ Товар не был удален ({ex})"

@sync_to_async
def product_pack_conf(product_id):
    try:
        a = Applications.objects.get(pk=product_id)
        a.status = "Упакован"
        a.save()
        return "✅ Товар успешно упакован и передан водителю"
    except Exception as ex: return "❌ " + str(ex)     

@sync_to_async
def report_info():
    try:
        r = Report.objects.get(pk=1)
        expectation = Applications.objects.filter(status="Ожидание подтверждения").count()
        confirmed = Applications.objects.filter(status="Подтвержден").count()
        canceled = Applications.objects.filter(status="Отменен").count()
        transferred = Applications.objects.filter(status="Передан упаковщику").count()
        transferred_dispatcher = Applications.objects.filter(status="Упакован").count()
        drive = Applications.objects.filter(status="В дороге").count()
        delivered = Applications.objects.filter(status="Доставлен").count() + int(r.delivered)
        matchs = Applications.objects.filter(status="Фабричный брак").count()
        matchs2 = Applications.objects.filter(status="Дорожный брак").count()

        text = f'''
Ожидающие подтверждения:  <b>{expectation}</b>
Подтвержденные:  <b>{confirmed}</b>
Отмененные:  <b>{canceled}</b>
Переданные Упаковщику:  <b>{transferred}</b>
Переданно диспетчеру:  <b>{transferred_dispatcher}</b>
В дороге:  <b>{drive}</b>
Дорожный брак: <b>{matchs2}</b>
Фабричный брак: <b>{matchs}</b>
Доставлено:  <b>{delivered}</b>
        '''

        return text
    except Exception as ex: return "❌ " + str(ex)

@sync_to_async
def confirm_product(product_id):
    try:
        p = Applications.objects.get(pk=product_id)
        p.status = "Подтвержден"
        p.save()
        return f"✅ Заказ <b>№{p.pk}</b> подтвержден"
    except Exception as ex: return "❌ " + str(ex)

@sync_to_async
def product_pack(product_id):
    try:
        p = Applications.objects.get(pk=product_id)
        p.status = "Передан упаковщику"
        p.save()
        return f"✅ Товар <b>№{p.pk}</b> Отправлен на Упаковку"
    except Exception as ex: return "❌ " + ex

@sync_to_async
def handover_product_to_drive(product_id, user_id):
    try:
        u = Profile.objects.get(user_id=user_id)
        p = Applications.objects.get(pk=product_id)
        p.status = "В дороге"
        p.driver = u
        p.save()
        return "✅ Заказ успешно принят"
    except Exception as ex: "❌ " + str(ex)

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
    except Exception as ex: "❌ " + str(ex)

@sync_to_async
def change_location(user_id, location):
    try:
        data = location.split(",")
        location = f"{data[-1]}, {data[5]}, {data[7]}"

        u = Profile.objects.get(user_id=user_id)
        p = Applications.objects.filter(status="В дороге", driver=u)

        for _ in p:
            _.location = location
            _.save()

        return "✅ Успешно"
    except Exception as ex: "❌ " + str(ex)

@sync_to_async
def applications_drivers():
    try:
        return Applications.objects.filter(status="В дороге")
    except: pass

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
def product_match(title, price, product_id, status):
    try:
        p = Applications.objects.get(pk=product_id)
        p.status = status
        p.save()
        Applications.objects.create(
            note=p.note,
            address=p.address,
            product=title,
            phone=p.phone,
            price=price,
            photo=p.photo,
            user=p.user,
            status="Упакован",
        )

        r = Report.objects.get(pk=1)
        r.delivered += 1
        r.save()

        return "✅ Успешно"
    except Exception as ex: return "❌ " + str(ex)

@sync_to_async
def drive_products():
    return Applications.objects.filter(status="В дороге")

@sync_to_async
def get_operators():
    return Profile.objects.filter(role="Оператор")


@sync_to_async
def find_products(info):
    p = Applications.objects.filter(pk=info)
    if len(p) >= 1:
        return p
    
    p = Applications.objects.filter(phone=info)
    if len(p) >= 1:
        return p

    return None

@sync_to_async
def get_money():

    a = Applications.objects.all()
    confirmed_request = Applications.objects.filter(status="Подтвержден")
    dispatcher = Applications.objects.filter(status="Упакован")
    packer = Applications.objects.filter(status="Передан упаковщику")
    driver = Applications.objects.filter(status="В дороге")

    total = 0
    total_packer = 0
    total_confirmed = 0
    total_dispatcher = 0
    total_driver = 0
    total_disp_pack_driv = 0

    for dr in driver:
        total_disp_pack_driv += int(dr.price)
        total_driver += int(dr.price)

    for p in packer:
        total_disp_pack_driv += int(p.price)
        total_packer += int(p.price)

    for d in dispatcher:
        total_disp_pack_driv += int(d.price)
        total_dispatcher += int(d.price)

    for i in confirmed_request:
        total_confirmed += int(i.price)

    for i in a:
        total += int(i.price)

    text = f'''
Итого 2,5% - <b>{round(total / 100 * 2.5, 10)} Рублей</b>
Объем, ₽ (Подтвержденные) - <b>{round(total_confirmed, 10)} Рублей</b>
Общий объем диспетчера, упаковщика, водителя ₽ - <b>{round(total_disp_pack_driv, 10)} Рублей</b>
Объем у диспетчера, ₽ - <b>{round(total_dispatcher, 10)} Рублей</b>
Объем у упаковщика, ₽ - <b>{round(total_packer, 10)} Рублей</b>
Объем в дороге, ₽ - <b>{round(total_driver, 10)} Рублей</b> 
    '''
    return text


@sync_to_async
def get_ojid_confirmed():
    return Applications.objects.filter(status="Ожидание подтверждения")

@sync_to_async
def get_confirmed():
    Applications.objects.filter(status="Подтвержден")

@sync_to_async
def get_canceled():
    return Applications.objects.filter(status="Отменен")

@sync_to_async
def get_packers():
    return Applications.objects.filter(status="Передан упаковщику")

@sync_to_async
def get_dispatchers():
    return Applications.objects.filter(status="Упакован")

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