import logging
import datetime
from random import randint
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes

from .config import API_TOKEN, admins
from .keyboard import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import Throttled

from loguru import logger as l
from geopy.geocoders import Nominatim
from fake_useragent import UserAgent

from aviato.models import *
from aviato.management.commands.db import *
from aviato.management.commands.keyboard import *

storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


class D(StatesGroup):
    user_id = State()
    code = State()
    name = State()
    note = State()
    note1 = State()
    address = State()
    prod = State()
    match = State()
    match2 = State()
    match3 = State()
    match4 = State()
    remake_request = State()
    edit_product = State()
    dist = State()
    dop_information = State()
    attach_check = State()
    dob_tovar = State()
    change_tovar = State()

    pr1 = State()
    pr2 = State()
    pr3 = State()
    pr4 = State()

    tv1 = State()
    tv2 = State()
    tv3 = State()
    tv4 = State()

    edit_request_1 = State()
    edit_request_2 = State()
    edit_request_3 = State()
    edit_request_4 = State()
    edit_request_5 = State()


async def count_bool(product):
    if product.bool_count:
        return "✅ Есть в наличии"
    return "❌ Нет в наличии ❌"

def get_direction1(product):
        if product.direction is None:
            return "Не указано";
        else: return product.direction   

async def get_message_from_product(product):
    cout_bool = await count_bool(product=product)
    products_text = ""
    def get_direction():
        if product.direction is None:
            return "Не указано";
        else: return product.direction   
    
    
    if "," in str(product.product):
        for i in str(product.product).replace('[', '').replace(']', '').split(','):
            products_text += f"{i}\n"
    else:
        for i in str(product.product).split(" "):
            products_text += f"{i}\n"


    text = (
        f"{cout_bool}\n"
        f"Примечание: {product.note}\nАдресс: {product.address}\n\n"
        f"Товар(ы): \n<b>{products_text}</b>\n"
        f"Цена: <code>{product.price}</code> рублей\nНомер: {product.phone}\n"
        f"Направление: <b>{get_direction()}</b>\n"
        f"Владелец товара: <b>@{product.user.username} ({product.user.role})</b>\n\n"
        f"ID: <code>{product.pk}</code>\nЛокация водителя: {str(product.location).replace('None', 'Неизвестно')}\n"
        f"Изменение локации было: <code>{str(product.time_update_location).split('.')[0]}</code>\n"
        f"Заявка создана: <code>{str(product.create_time).split('.')[0]}</code>\n"
    )

    return text.replace("'", "")


async def get_menu(message):
    user = await get_user_or_create(
        user_id=str(message.from_user.id), username=message.from_user.username
    )

    text = f"""
Добрый день, {message.from_user.first_name}! Мы рады приветствовать Вас в чат-боте
<b>«RUKEA»</b>!

Для выбора интересующего вас раздела воспользуйтесь кнопками из меню ниже 👇

👁 Если вы не видите внизу кнопки меню, нажмите сюда /start
"""
    if message.chat.id in admins:
        await message.answer(text, reply_markup=admin_menu())

    elif user.role == "Снабженец":
        await message.answer(text, reply_markup=supplier_menu())

    elif user.role == "Админ":
        await message.answer(text, reply_markup=admin_menu())

    elif user.role == "Менеджер":
        await message.answer(text, reply_markup=manager_menu())

    elif user.role == "Оператор":
        await message.answer(text, reply_markup=operator_menu())

    elif user.role == "Логист":
        await message.answer(text, reply_markup=logist_menu())

    elif user.role == "Упаковщик":
        await message.answer(text, reply_markup=packer_menu())

    elif user.role == "Водитель":
        await message.answer(text, reply_markup=driver_menu())

    else:
        await message.answer(
            f"{message.from_user.first_name} 👋, \n\nу вас нет роли, напишите команду /code и введите код"
        )


async def get_menu_call(call):
    user = await get_user_or_create(
        user_id=str(call.message.chat.id), username=call.message.from_user.username
    )
    if call.message.chat.id in admins:
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=admin_menu()
        )

    elif user.role == "Снабженец":
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=admin_menu()
        )

    elif user.role == "Админ":
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=admin_menu()
        )

    elif user.role == "Менеджер":
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=manager_menu()
        )

    elif user.role == "Оператор":
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=operator_menu()
        )

    elif user.role == "Логист":
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=logist_menu()
        )

    elif user.role == "Упаковщик":
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=packer_menu()
        )

    elif user.role == "Водитель":
        await call.message.answer(
            f"🔙 Вы перемещены в главное меню", reply_markup=driver_menu()
        )


async def cloud():
    try:
        products = await drive_products()
        for product in products:
            time = int(str(product.time_update_location).split(" ")[1].split(":")[0])
            current_time = int(str(datetime.datetime.now()).split(" ")[1].split(":")[0])
            every_hours = current_time - time - 3
            if every_hours > 6:
                if product.status == "В дороге":
                    await bot.send_message(
                        product.user.user_id, "❗ Обновите свою геолокацию"
                    )
            if every_hours > 20:
                if product.status == "Ожидание подтверждения":
                    operators = await get_operators()
                    for operator in operators:
                        await bot.send_message(
                            operator.user_id, "❗ У вас есть необработанныее заказы"
                        )

                elif product.status == "Упакован":
                    logists = await get_logists()
                    for logist in logists:
                        await bot.send_message(
                            logist.user_id, "❗ У вас есть необработанныее заказы"
                        )

                elif product.status == "Ожидает упаковки":
                    packers = await get_all_packers()
                    for packer in packers:
                        await bot.send_message(
                            packer.user_id, "❗ У вас есть необработанныее заказы"
                        )

        a = Applications.objects.all()
        for application in a:
            prod = application.products.all()
            for produc in prod:
                if produc.count >= 0:
                    application.bool_count = True
                    application.save()
                else:
                    application.bool_count = False
                    application.save()
                    continue

    except Exception as ex:
        l.error(ex)


@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await cloud()
    await get_menu(message)



@dp.message_handler(text="👤 Сотрудники", state="*")
async def employees(message: types.Message):
    users = await get_all_users()
    text = ""
    for user in users:
        text += f"Телеграм: @{user.username}\nДолжность: {user.role}\nID: {user.user_id}\n\n"
    text = text.replace("@None", "Отстутсвует username")
    text += f"\n<b>Количество сотрудников: {len(users)}</b>"
    await message.answer(text, reply_markup=employees_inline_menu())
    await cloud()


@dp.callback_query_handler(text_startswith="add_employees", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Выберите роль будущего сотрудника:", reply_markup=employees_role_inline()
    )
    await cloud()

@dp.callback_query_handler(text_startswith="supplier_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
    code = randint(100, 999)
    await create_code_employees(
        user_id=call.message.chat.id, code=code, role="Снабженец"
    )
    await get_menu_call(call)
    await call.message.answer(
        f"Код чтобы получить статус <b>Снабженец</b> в боте\n\nКод: <code>{code}</code>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="admin_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
    code = randint(100, 999)
    await create_code_employees(user_id=call.message.chat.id, code=code, role="Админ")
    await get_menu_call(call)
    await call.message.answer(
        f"Код чтобы получить статус <b>Админа</b> в боте\n\nКод: <code>{code}</code>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="manager_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
    code = code = randint(100, 999)
    await create_code_employees(
        user_id=call.message.chat.id, code=code, role="Менеджер"
    )
    await get_menu_call(call)
    await call.message.answer(
        f"Код чтобы получить статус <b>Менеджера</b> в боте\n\nКод: <code>{code}</code>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="logist_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
    code = randint(100, 999)
    await create_code_employees(user_id=call.message.chat.id, code=code, role="Логист")
    await get_menu_call(call)
    await call.message.answer(
        f"Код чтобы получить статус <b>Логист</b> в боте\n\nКод: <code>{code}</code>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="operator_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
    code = randint(100, 999)
    await create_code_employees(
        user_id=call.message.chat.id, code=code, role="Оператор"
    )
    await get_menu_call(call)
    await call.message.answer(
        f"Код чтобы получить статус <b>Оператора</b> в боте\n\nКод: <code>{code}</code>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="driver_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
    code = randint(100, 999)
    await create_code_employees(
        user_id=call.message.chat.id, code=code, role="Водитель"
    )
    await get_menu_call(call)
    await call.message.answer(
        f"Код чтобы получить статус <b>Водителя</b> в боте\n\nКод: <code>{code}</code>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="packer_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
    code = randint(100, 999)
    await create_code_employees(
        user_id=call.message.chat.id, code=code, role="Упаковщик"
    )
    await get_menu_call(call)
    await call.message.answer(
        f"Код чтобы получить статус <b>Упаковщик</b> в боте\n\nКод: <code>{code}</code>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="remove_employees", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer("🆔 Введите ID человека у которого хотите изменить роль:")
    await D.user_id.set()
    await cloud()


@dp.message_handler(state=D.user_id)
async def dasdasdsa2(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        user = await get_user_or_error(user_id=str(message.text))
        if user == "Error":
            await message.answer("❌ Такой пользоватлеь не найден")
        else:
            inlineh1 = types.InlineKeyboardMarkup()

            inlineh1.row(
                    types.InlineKeyboardButton("🗳️ Логист", callback_data="remove_logist_r"), 
                    types.InlineKeyboardButton("👷‍♂️ Снабженец", callback_data="remove_snabj_r")
                )

            inlineh1.row(
                types.InlineKeyboardButton(
                    "🛡️ Админ", callback_data=f"remove_admin:{user.user_id}"
                ),
                types.InlineKeyboardButton(
                    "⭐ Менеджер", callback_data=f"remove_manager:{user.user_id}"
                ),
            )
            inlineh1.row(
                types.InlineKeyboardButton(
                    "👨‍💻 Оператор", callback_data=f"remove_operator:{user.user_id}"
                ),
                types.InlineKeyboardButton(
                    "🔧 Водитель", callback_data=f"remove_driver:{user.user_id}"
                ),
            )
            inlineh1.row(
                types.InlineKeyboardButton(
                    "⚙️ Упаковщик", callback_data=f"remove_packer:{user.user_id}"
                )
            )
            await message.answer(
                f"Имя: @{user.username}\nID: {user.user_id}\nРоль: {user.role}\n\nВыберите роль для пользователя",
                reply_markup=inlineh1,
            )
    else:
        await message.answer("❌ Неравильно введен ID")
    await state.finish()
    await cloud()


@dp.callback_query_handler(text_startswith="remove_snabj_r")
async def handler(call: types.CallbackQuery):
    user_id = call.data.split(":")[1]
    user = await change_role_user(user_id=str(user_id), role="Снабженец")
    await get_menu_call(call)
    await call.message.answer(
        "✅ Успешно поменял роль сотрудника на роль: <b>Снабженец</b>"
    )
    await cloud()

@dp.callback_query_handler(text_startswith="remove_logist_r")
async def handler(call: types.CallbackQuery):
    user_id = call.data.split(":")[1]
    user = await change_role_user(user_id=str(user_id), role="Логист")
    await get_menu_call(call)
    await call.message.answer(
        "✅ Успешно поменял роль сотрудника на роль: <b>Логист</b>"
    )
    await cloud()

@dp.callback_query_handler(text_startswith="remove_admin", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    user = await change_role_user(user_id=str(user_id), role="Админ")
    await get_menu_call(call)
    await call.message.answer(
        "✅ Успешно поменял роль сотрудника на роль: <b>Админа</b>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="remove_manager", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    user = await change_role_user(user_id=str(user_id), role="Менеджер")

    await get_menu_call(call)
    await call.message.answer(
        "✅ Успешно поменял роль сотрудника на роль: <b>Менеджера</b>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="remove_operator", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    user = await change_role_user(user_id=str(user_id), role="Оператор")

    await get_menu_call(call)

    await call.message.answer(
        "✅ Успешно поменял роль сотрудника на роль: <b>Оператора</b>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="remove_driver", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    user = await change_role_user(user_id=str(user_id), role="Водитель")
    await get_menu_call(call)
    await call.message.answer(
        "✅ Успешно поменял роль сотрудника на роль: <b>Водителя</b>"
    )
    await cloud()


@dp.callback_query_handler(text_startswith="remove_packer", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    user = await change_role_user(user_id=str(user_id), role="Упаковщик")
    await get_menu_call(call)
    await call.message.answer(
        "✅ Успешно поменял роль сотрудника на роль: <b>Упаковщика</b>"
    )
    await cloud()


@dp.message_handler(commands=["code"], state="*")
async def code(message: types.Message):
    await message.answer("🆔 Введите код чтобы получить роль в боте: ")
    await D.code.set()
    await cloud()


@dp.message_handler(state=D.code)
async def code(message: types.Message, state: FSMContext):
    text = await find_code_and_apply(user_id=message.from_user.id, code=message.text)
    await message.answer("Введите ваше Имя, Фамилию")
    await D.name.set()
    await cloud()


@dp.message_handler(state=D.name)
async def code(message: types.Message, state: FSMContext):
    name = f"{message.text}"
    await change_name(user_id=str(message.from_user.id), name=name)
    await message.answer("Успешно добавил вас в базу.")
    await state.finish()
    await get_menu(message)
    await cloud()


@dp.message_handler(text="✍ Добавить заявку", state="*")
async def userrequests(message: types.Message, state: FSMContext):
    await message.answer("🎤 Выберите вид добавления заявки: ", reply_markup=get_choice_application())


# bez_product
@dp.callback_query_handler(text_startswith="bez_product", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "🖋 Заполните и отправьте следующий шаблон\n\nТовар\nАдрес\nНомер (только цифры)\nЦена (число)\nПримечание\n\nЧтобы отменить загрузку товара напишите /start"
    )
    await D.note1.set()
    await cloud()

@dp.message_handler(state=D.note1)
async def userrequests(message: types.Message, state: FSMContext):
    data = message.text.split("\n")
    text = await product_save_bez(user_id=str(message.from_user.id), data=data)
    try:
        operators = await get_operators()
        for operator in operators:
            await bot.send_message(
                operator.user_id, "⌛ У вас есть необработанный заказ"
            )
    except:
        pass
    await state.finish()
    await message.answer(text)
    await cloud()


@dp.callback_query_handler(text_startswith="s_product", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        "🖋 Заполните и отправьте следующий шаблон\n\nТовар\nАдрес\nНомер (только цифры)\nЦена (число)\nПримечание\n\nЧтобы отменить загрузку товара напишите /start"
    )
    await D.note.set()
    await cloud()


@dp.message_handler(state=D.note)
async def userrequests(message: types.Message, state: FSMContext):
    await message.delete()
    data = message.text.split("\n")
    text = await product_save(user_id=str(message.from_user.id), data=data)
    try:
        operators = await get_operators()
        for operator in operators:
            await bot.send_message(
                operator.user_id, "⌛ У вас есть необработанный заказ"
            )
    except:
        pass
    await state.finish()
    await message.answer(text)
    await cloud()


@dp.message_handler(text="📔 Заявки", state="*")
async def employees(message: types.Message):
    products = await get_confirm_products()
    if len(products) >= 1:
        for product in products:

            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    "❌  Отменить заявку", callback_data=f"remove_request:{product.pk}"
                )
            )
            inlineh1.row(
                types.InlineKeyboardButton(
                    "✅  Подтвердить заявку",
                    callback_data=f"confirm_request:{product.pk}",
                )
            )
            inlineh1.row(
                types.InlineKeyboardButton(
                    "✍  Добавить информацию о доставке",
                    callback_data=f"dop_information:{product.pk}",
                )
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")


            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("Пока нет заявок.")
    await cloud()


@dp.message_handler(text="📔 Все Заявки", state="*")
async def employees(message: types.Message):
    products = await get_products()
    if len(products) >= 1:
        for product in products:
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    "❌ Удалить заявку", callback_data=f"remove_request:{product.pk}"
                )
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("Пока нет заявок.")
    await cloud()


@dp.callback_query_handler(text_startswith="dop_information", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await D.dop_information.set()
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer("✍ Введите дополнительную информацию о доставке:")


@dp.message_handler(state=D.dop_information)
async def employees(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dop_information = message.text
    product_id = data["product_id"]
    text = await set_dop_information(text=dop_information, product_id=product_id)
    await message.answer(text)
    await state.finish()

    product = await get_product(product_id=product_id)
    cout_bool = await count_bool(product=product)
    text = await get_message_from_product(product)
    inlineh1 = types.InlineKeyboardMarkup()
    inlineh1.row(
        types.InlineKeyboardButton(
            "❌  Отменить заявку", callback_data=f"remove_request:{product.pk}"
        )
    )
    inlineh1.row(
        types.InlineKeyboardButton(
            "✅  Подтвердить заявку", callback_data=f"confirm_request:{product.pk}"
        )
    )
    inlineh1.row(
        types.InlineKeyboardButton(
            "✍  Добавить информацию о доставке",
            callback_data=f"dop_information:{product.pk}",
        )
    )

    photos = [ph.photo for ph in product.products.all()]
    inlineh2 = types.InlineKeyboardMarkup()
    inlineh2.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
    for p in photos:
        try:
            await message.answer_photo(photo=p, reply_markup=inlineh2)
        except:
            pass
    if product.checks_document is None:
        pass
    else:
        try:
            await message.answer_photo(
                photo=open(product.checks_document, "rb"),
                reply_markup=inlineh2,
                caption="Чек",
            )
        except: await message.answer("❌ Чек не найден")
    await message.answer(text, reply_markup=inlineh1)


# Добавить показ товара вновь


@dp.callback_query_handler(text_startswith="confirm_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1] ##################################################################################################
    text = await confirm_product(product_id=product_id)
    try:
        packers = await get_all_packers()
        for packer in packers:
            await bot.send_message(packer.user_id, "⌛ У вас есть необработанный заказ")
    except:
        pass
    await get_menu_call(call)
    await call.message.delete()
    await call.message.answer(text)
    await cloud()


@dp.callback_query_handler(text_startswith="remove_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    text = await delete_product(product_id=product_id)
    await get_menu_call(call)
    await call.message.delete()
    await call.message.answer(text)
    await cloud()


@dp.message_handler(text="💡 Ожидающие чека", state="*")
async def dfs13fdsv(message: types.Message, state: FSMContext):
    products = await get_all_ojid_check()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    "🧾 Прикрепить чек", callback_data=f"attach_check:{product.pk}"
                )
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("❌ Ничего не найдено")


@dp.callback_query_handler(text_startswith="attach_check", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    product_id = call.data.split(":")[1]
    await D.attach_check.set()
    await state.update_data(product_id=product_id)
    await call.message.answer("Пришлите чек 🧾")


@dp.message_handler(content_types=ContentTypes.DOCUMENT, state=D.attach_check)
async def doc_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    path = f"media/documents/{message.from_user.id}_{message.message_id}.pdf"
    if document := message.document:
        await document.download(
            destination_file=f"media/documents/{message.from_user.id}_{message.message_id}.pdf",
        )
        await set_path_file(product_id=data["product_id"], path=path)
        await message.answer("✅ Успешно сохранил документ")
    else:
        await message.asnwer("❌ Отправьте PDF документ!")
    await state.finish()


@dp.message_handler(text="📕 Отчет", state="*")
async def employees(message: types.Message):
    answer = await report_info()
    user = await get_user_or_create(user_id=str(message.from_user.id))

    inlineh1 = types.InlineKeyboardMarkup()
    inlineh1.row(
        types.InlineKeyboardButton(
            "📫 Ожидающие подтверждения", callback_data="ojid_confirmed"
        )
    )
    inlineh1.row(
        types.InlineKeyboardButton("📮 Подтвержденные", callback_data="oj_confirmd"),
        types.InlineKeyboardButton("📪 Отмененные", callback_data="oj_canceled"),
    )
    inlineh1.row(
        types.InlineKeyboardButton(
            "👨‍💻 Переданные диспетчеру", callback_data="oj_dispatcher"
        ),
        types.InlineKeyboardButton("🚗 В дороге", callback_data="oj_drive"),
    )
    inlineh1.row(
        types.InlineKeyboardButton(
            "❗ Нет в наличии ❗", callback_data="oj_net_v_nalichii"
        )
    )
    inlineh1.row(
        types.InlineKeyboardButton(
            "📦 Упакованные", callback_data="oj_net_logist"
        )
    )
    inlineh1.row(
        types.InlineKeyboardButton("❌ Дорожный брак", callback_data="oj_dorozh_brak"),
        types.InlineKeyboardButton("❌ Фабричный брак", callback_data="oj_fabr_brak"),
    )
    inlineh1.row(
        types.InlineKeyboardButton("✅ Доставлено", callback_data="oj_delevired"),
        types.InlineKeyboardButton("❎ Ожидающие товары", callback_data="oj_pr"),
    )

    inlineh1.row(
        types.InlineKeyboardButton(
            "👷‍♂️ Переданные на упаковку", callback_data="oj_packer"
        )
    )

    await message.answer(answer, reply_markup=inlineh1)
    await cloud()


@dp.message_handler(text="❗ Нет в наличии ❗", state="*")
async def dfsfdslf(message: types.Message, state: FSMContext):
    await state.finish()
    products = await net_v_nalichii()
    if len(products) >= 1:
        for product in products:
            orig_product = product.products.all()
            text = ""
            for t in orig_product:
                text += f"Товар: {t.product}\nКоличество: {t.count}\n\n"

            txt = await get_message_from_product(product)
            text += txt

            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("❌ Ничего не найдено")


# Нет у логиста
@dp.callback_query_handler(text_startswith="oj_net_logist")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await net_v_nalichii_logist()

    if len(products) >= 1:
        for product in products:
            orig_product = product.products.all()
            text = ""
            for t in orig_product:
                text += f"Товар: {t.product}\nКоличество: {t.count}\n\n"

            txt = await get_message_from_product(product)
            text += txt

            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass

            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# Нет в наличии
@dp.callback_query_handler(text_startswith="oj_net_v_nalichii", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await net_v_nalichii()

    if len(products) >= 1:
        for product in products:
            orig_product = product.products.all()
            text = ""
            for t in orig_product:
                text += f"Товар: {t.product}\nКоличество: {t.count}\n\n"

            txt = await get_message_from_product(product)
            text += txt

            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass

            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# Ожидающие товары oj_pr
@dp.callback_query_handler(text_startswith="oj_pr", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await oj_pr()

    if len(products) >= 1:
        for product in products:
            text = (
                f"Товар: {product}\nКоличество: {product.count}\n"
                f"Оптовая цена: {product.opt_price}\nНа сумму: {product.product_suum}\n"
                f"2.5% от Суммы Товара: {product.product_percent}"
            )
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = product.photo
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            if None is photos:
                pass
            else:
                await call.message.answer_photo(photo=photos, reply_markup=inlineh2)
            await call.message.answer(text, reply_markup=inlineh1)
    else:
        await call.message.answer("❌ Ничего не найдено")


# Доставлено
@dp.callback_query_handler(text_startswith="oj_delevired", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await oj_delivered()

    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        pass


# Фабричный брак
@dp.callback_query_handler(text_startswith="oj_fabr_brak", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await fabr_brack_products()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# Дорожный брак
@dp.callback_query_handler(text_startswith="oj_dorozh_brak", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await dorozh_brak_products()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# В дороге
@dp.callback_query_handler(text_startswith="oj_drive", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await get_drive_pr()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# Переданные диспетчеру
@dp.callback_query_handler(text_startswith="oj_dispatcher", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await get_dispatchers()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# Переданные Упаковщику
@dp.callback_query_handler(text_startswith="oj_packer", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await get_packers()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# Отмененные
@dp.callback_query_handler(text_startswith="oj_canceled", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await get_canceled()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


# 
@dp.callback_query_handler(text_startswith="oj_confirmd", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await get_confirmed()
    if products is None:
        await call.message.answer("❌ Ничего не найдено")
    else:
        if len(products) >= 1:
            for product in products:
                cout_bool = await count_bool(product=product)
                text = await get_message_from_product(product)
                inlineh1 = types.InlineKeyboardMarkup()
                inlineh1.row(
                    types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
                )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

        else:
            await call.message.answer("❌ Ничего не найдено")


# Ожидающие подтверждения
@dp.callback_query_handler(text_startswith="ojid_confirmed", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    products = await get_ojid_confirmed()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await call.message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await call.message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await call.message.answer("❌ Чек не найден")
            await call.message.answer(text, reply_markup=inlineh1)

    else:
        await call.message.answer("❌ Ничего не найдено")


@dp.message_handler(text="📚 Упакованные", state="*")
async def employees(message: types.Message):
    products = await get_confirmed_products()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    "✅ Ввести направление",
                    callback_data=f"confirmed_request:{product.pk}",
                )
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("Пока нет подтвержденных заявок.")
    await cloud()


@dp.callback_query_handler(text_startswith="confirmed_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    product_id = call.data.split(":")[1]

    await state.update_data(product_id=product_id)

    await call.message.answer("✍ Введите направление: ")
    await D.dist.set()


@dp.message_handler(state=D.dist)
async def add_employe(message: types.Message, state: FSMContext):
    try:
        packers = await get_all_packers()
        for packer in packers:
            await bot.send_message(packer.user_id, "⌛ У вас есть необработанный заказ")
    except Exception as ex:
        l.critical(ex)

    data = await state.get_data()
    dist = message.text
    text = await product_pack(product_id=data["product_id"], dist=dist)

    await get_menu(message)
    await message.answer(text)
    await state.finish()
    await cloud()


# peredan_dispatcher
@dp.callback_query_handler(text_startswith="peredan_dispatcher")
async def handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    product_id = call.data.split(":")[1]
    text = await product_pack_conf(product_id=product_id)
    await call.message.answer(text)
    await cloud()
    await get_menu_call(call=call)

    try:
        logists = await get_logists()
        for logist in logists:
            await bot.send_message(
                logist.user_id,
                "❗ У вас есть необработанныее заказы",
            )
    except:
        pass

@dp.message_handler(text="📊 Неотправленные", state="*")
async def employees(message: types.Message):
    products = await get_packers()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                    types.InlineKeyboardButton("✅ Передать диспетчеру", callback_data=f"peredan_dispatcher:{product.pk}"),
                    types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("❌ Ничего не найдено")




@dp.message_handler(text="⚡ Неупокованные заказы", state="*")
async def employees(message: types.Message):
    products = await get_pack_products()
    if len(products) >= 1:
        for product in products:
            text = f"ID: {product.pk}\nНаправление: <b>{get_direction1(product)}</b>\nАдресс: {product.address}\nТовар: {product.product}\n"
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    "✅ Упакован",
                    callback_data=f"product_pack_logist:{product.pk}",
                )
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("Пока нет заявок для упаковки.")
    await cloud()

# Передан логисту
@dp.callback_query_handler(text_startswith="product_pack_logist")
async def handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    product_id = call.data.split(":")[1]
    text = await product_pack_logist(product_id=product_id)
    await call.message.answer(text)

    try:
        logists = await get_logists()
        for logist in logists:
            await bot.send_message(
                logist.user_id,
                "❗ У вас есть необработанныее заказы",
            )
    except:
        pass

    await get_menu_call(call=call)


@dp.callback_query_handler(text_startswith="confirmed2_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    text = await product_pack_conf(product_id=product_id)
    try:
        logists = await get_logists()
        for logist in logists:
            await bot.send_message(
                logist.user_id,
                "❗ У вас есть необработанныее заказы",
            )
    except:
        pass
    await get_menu_call(call)
    await call.message.answer(text)
    await cloud()


@dp.callback_query_handler(text_startswith="confirmed_drive_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    text = await handover_product_to_drive(
        product_id=product_id, user_id=str(call.message.chat.id)
    )
    await get_menu_call(call)
    await call.message.answer(text)
    await cloud()


@dp.message_handler(text="🚙 Активные заказы", state="*")
async def employees(message: types.Message):
    products = await get_active_requests_drive(user_id=message.from_user.id)

    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    "✅ Я доставил этот заказ",
                    callback_data=f"conf_r_request:{product.pk}",
                )
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("У вас нет активных заявок на доставку.")
    await cloud()


@dp.callback_query_handler(text_startswith="conf_r_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    text = await delivered(product_id=product_id)
    await get_menu_call(call)
    await call.message.answer(text)
    await cloud()


@dp.message_handler(content_types=["location"])
async def employees(message: types.Message):
    latitude = message.location["latitude"]
    longitude = message.location["longitude"]

    ua = UserAgent()
    random_user_agent = ua.random
    locator = Nominatim(user_agent=random_user_agent)
    location = locator.reverse(f"{latitude}, {longitude}")

    try:
        admin_list = await admins_list()
        for admin in admin_list:
            await bot.send_message(admin.user_id, "✅ Водитель обновил свою геолокацию")
    except:
        pass

    city = location.raw["address"]["city"]
    region = location.raw["address"]["state"]

    text = f"{city}, {region}"
    text1 = await change_location(user_id=message.from_user.id, location=text)
    await get_menu(message)
    await message.answer(text1)
    await cloud()


@dp.message_handler(text="🚓 Активные заказы водителей", state="*")
async def employees(message: types.Message):
    products = await applications_drivers()
    if products:
        for product in products:
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    "🗺 Получить геолокацию", callback_data=f"location_dr:{product.pk}"
                )
            )
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("❌ Товары отсутствуют")
    await cloud()


@dp.callback_query_handler(text_startswith="location_dr", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    product = await plea_location(product_id=product_id)
    await bot.send_message(
        product.driver.user_id,
        '<b>❗❗ Администратор просит вас отправить вашу геолокацию нажав на кнопку "Отправить свою локацию 🗺️"</b>',
    )
    await call.message.answer("✅ Отправил запрос на получение геолокации водителя")
    await cloud()


@dp.message_handler(commands=["product"], state="*")
async def start(message: types.Message, state: FSMContext):
    await message.answer("🆔 Введите ID товара: ")
    await D.prod.set()
    await cloud()


@dp.message_handler(state=D.prod)
async def employees(message: types.Message, state: FSMContext):
    product_id = message.text
    product = await find_product(product_id=product_id)
    inlineh1 = types.InlineKeyboardMarkup()
    inlineh1.row(
        types.InlineKeyboardButton(
            "🗺 Получить геолокацию", callback_data=f"location_dr:{product.pk}"
        )
    )
    cout_bool = await count_bool(product=product)
    if product.status == "Доставлен" or "В дороге" == product.status:
        text = f"Информация о доставке: {str(product.delivery_information).replace('None', 'Отсутствует')}\nПримечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\nНаправление: <b>{get_direction1(product)}</b>\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Неизвестно')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}\nСтатус заявки: {product.status}\n{cout_bool}"
    else:
        text = f"Информация о доставке: {str(product.delivery_information).replace('None', 'Отсутствует')}\nПримечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nЗагрузил товар: @{product.user.username} ({product.user.role})\nНаправление: <b>{get_direction1(product)}</b>\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Неизвестно')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}\nСтатус заявки: Подготавливается к отправке\n{cout_bool}"

    await message.answer(text, reply_markup=inlineh1)
    await cloud()


@dp.message_handler(text="📢 Логистика", state="*")
async def employees(message: types.Message):
    products = await pack_to_logist()
    if len(products) >= 1:
        for product in products:
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)

            drivers = await get_all_drivers()
            inlineh1 = types.InlineKeyboardMarkup()

            if drivers.count() > 0:
                for driver in drivers:
                    inlineh1.row(
                        types.InlineKeyboardButton(
                            f"🚗 {driver.first_name}",
                            callback_data=f"driv:{driver.pk}:{product.pk}",
                        )
                    )
            else:
                inlineh1.row(
                    types.InlineKeyboardButton(
                        f"❌ Водители отсутствуют", callback_data=f"dsdsdriv"
                    )
                )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)

    else:
        await message.answer("Пока нет упакованных заявок.")
    await cloud()


@dp.callback_query_handler(text_startswith="driv", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.split(":")[1]
    product_id = call.data.split(":")[2]

    product = await get_product(product_id=product_id)
    user = await get_user(user_id=str(user_id))
    user_id = user.user_id

    if product:
        if product.delivery_information:
            text = (
                f"Товар: {str(product.product).replace('[', '').replace(']', '')}\n"
                f"Цена: {product.price}\nАдрес: {product.address}\n"
                f"Номер: {product.phone}\n"
                f"Информация о доставке: ✅ {product.delivery_information}\n"
            ).replace("'", "")        
        else: 
            text = (
                f"Товар: {str(product.product).replace('[', '').replace(']', '')}\n"
                f"Цена: {product.price}\nАдрес: {product.address}\n"
                f"Номер: {product.phone}\n"
                f"Информация о доставке: ❌ Отсутствует ❌"
            ).replace("'", "")   


        inlineh1 = types.InlineKeyboardMarkup()
        inlineh1.row(
            types.InlineKeyboardButton(
                f"✅ Принять заказ", callback_data=f"dr_confirmed:{user_id}:{product_id}"
            )
        )

        photos = [ph.photo for ph in product.products.all()]
        inlineh2 = types.InlineKeyboardMarkup()
        inlineh2.row(
            types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
        )
        for p in photos:
            try:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=str(p),
                    caption=text,
                    reply_markup=inlineh2,
                )
            except:
                pass
        await bot.send_message(chat_id=user_id, text=text, reply_markup=inlineh1)

        await call.message.delete()
        await call.message.answer("✅ Успешно")
    else:
        await call.message.answer(
            "❌ Такой товар уже не существуют, возможно его кто то удалил"
        )
    await cloud()


@dp.callback_query_handler(text_startswith="dr_confirmed", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):

    user_id = call.data.split(":")[1]
    product_id = call.data.split(":")[2]

    user = await get_user_userId(user_id=user_id)
    product = await get_product(product_id=product_id)

    product = await driver_confrimed(user=user, product=product)
    await call.message.answer("✅ Успешно приняли заказ")
    await state.finish()
    await get_menu_call(call)
    await call.message.delete()
    await call.message.answer("✅ Успешно")
    await cloud()


@dp.message_handler(text="⚒ Браки", state="*")
async def employees(message: types.Message):
    await message.answer("🆔 Введите ID бракованного товара: ")
    await D.match.set()
    await cloud()


@dp.message_handler(state=D.match)
async def employees(message: types.Message, state: FSMContext):
    try:
        products = await find_products(info=message.text)
        for product in products:
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    f"✨ Фабричный брак", callback_data=f"product_brak_f:{product.pk}"
                ),
                types.InlineKeyboardButton(
                    f"✨ Дорожный брак", callback_data=f"product_brak_d:{product.pk}"
                ),
            )
            inlineh1.row(
                types.InlineKeyboardButton(f"Скрыть", callback_data="message_hide")
            )
            cout_bool = await count_bool(product=product)
            text = await get_message_from_product(product)
            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass
            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")
            await message.answer(text, reply_markup=inlineh1)
    except Exception as ex:
        await message.answer(f"❌ Товар не найден ({ex})")
    await state.finish()
    await cloud()


@dp.callback_query_handler(text_startswith="message_hide", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await cloud()


@dp.callback_query_handler(text_startswith="product_brak_d", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await D.match3.set()
    await state.update_data(product_id=product_id)
    await call.message.answer(
        "Отправьте сообщениее по следующему шаблону\n\nНовый товар\nНовая Цена (в цифрах)\nСтарый Товар\nСтарая Цена (в цифрах)"
    )
    await cloud()


@dp.message_handler(state=D.match3)
async def employees(message: types.Message, state: FSMContext):
    _ = await state.get_data()
    data = message.text.split("\n")

    product_title = data[0]
    product_price = data[1]

    product_title2 = data[2]
    product_price2 = data[3]

    product_id = _["product_id"]

    text = await product_match(
        title=product_title,
        price=product_price,
        title2=product_title2,
        price2=product_price2,
        product_id=product_id,
        status="Дорожный брак",
    )
    await message.answer(text)
    await state.finish()
    await get_menu(message)
    await cloud()


@dp.callback_query_handler(text_startswith="product_brak_f", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await D.match2.set()
    await state.update_data(product_id=product_id)
    await call.message.answer(
        "Отправьте сообщениее по следующему шаблону\n\nНовый товар\nНовая Цена (в цифрах)\nСтарый Товар\nСтарая Цена (в цифрах)"
    )
    await cloud()


@dp.message_handler(state=D.match2)
async def employees(message: types.Message, state: FSMContext):
    _ = await state.get_data()
    data = message.text.split("\n")

    product_title = data[0]
    product_price = data[1]

    product_title2 = data[2]
    product_price2 = data[3]

    product_id = _["product_id"]

    text = await product_match(
        title=product_title,
        price=product_price,
        title2=product_title2,
        price2=product_price2,
        product_id=product_id,
        status="Фабричный брак",
    )
    await message.answer(text)
    await state.finish()
    await get_menu(message)
    await cloud()


@dp.message_handler(text="🌏 Поиск заявок", state="*")
async def employees(message: types.Message, state: FSMContext):
    await message.answer("Введите ID заказа или номер телефона")
    await cloud()
    await D.remake_request.set()


@dp.message_handler(state=D.remake_request)
async def efdsfsdff(message: types.Message, state: FSMContext):
    text = message.text
    products = await find_products(info=text)
    if products is None:
        await message.answer("❌ Не найдено")
        await state.finish()
    else:
        for product in products:
            inlineh1 = types.InlineKeyboardMarkup()
            inlineh1.row(
                types.InlineKeyboardButton(
                    f"🖋 Редактировать заявку",
                    callback_data=f"edit_request:{product.pk}",
                )
            )
            inlineh1.row(
                types.InlineKeyboardButton(
                    f"♻ Скрыть заявку", callback_data=f"hide_message"
                )
            )

            photos = [ph.photo for ph in product.products.all()]
            inlineh2 = types.InlineKeyboardMarkup()
            inlineh2.row(
                types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide")
            )
            for p in photos:
                try:
                    await message.answer_photo(photo=p, reply_markup=inlineh2)
                except:
                    pass

            if product.checks_document is None:
                pass
            else:
                try:
                    await message.answer_photo(
                        photo=open(product.checks_document, "rb"),
                        reply_markup=inlineh2,
                        caption="Чек",
                    )
                except: await message.answer("❌ Чек не найден")

            cout_bool = await count_bool(product=product)
            text = f"Информация о доставке: {str(product.delivery_information).replace('None', 'Отсутствует')}\nАдресс: <b>{product.address}</b>\nТовар: <b>{product.product}</b>\nЦена: <b>{product.price}</b>\nНомер: <b>{product.phone}</b>\nВладелец товара: <b>@{product.user.username} ({product.user.role})</b>\nПримечание: <b>{product.note}</b>\nНаправление: <b>{get_direction1(product)}</b>\n\nID: <b>{product.pk}</b>\nСтатуc: <b>{product.status}</b>\nЛокация водителя: <b>{str(product.location).replace('None', 'Неизвестно')}</b>\nИзменение локации было в: <b>{str(product.time_update_location).split('.')[0]}</b>\n{cout_bool}"
            await message.answer(text, reply_markup=inlineh1)
            await state.finish()


@dp.callback_query_handler(text_startswith="hide_message", state="*")
async def fdfdsfd13(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("✅ Успешно")


@dp.callback_query_handler(text_startswith="edit_request", state="*")
async def fdsf31fkx1(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    product_id = call.data.split(":")[1]
    product = await get_product(product_id=product_id)
    text = (
        await get_message_from_product(product=product)
        + "\n\n<b>Выберите что изменить:</b>"
    )

    inline_kb_full = types.InlineKeyboardMarkup()
    inline_kb_full.row(
        types.InlineKeyboardButton(
            "Товар", callback_data=f"edit_product1:{product_id}"
        ),
        types.InlineKeyboardButton(
            "Примечание", callback_data=f"edit_note1:{product_id}"
        ),
    )
    inline_kb_full.row(
        types.InlineKeyboardButton(
            "Адрес", callback_data=f"edit_address1:{product_id}"
        ),
        types.InlineKeyboardButton("Цена", callback_data=f"edit_price1:{product_id}"),
    )
    inline_kb_full.row(
        types.InlineKeyboardButton("Номер", callback_data=f"edit_phone1:{product_id}")
    )
    await call.message.answer(text, reply_markup=inline_kb_full)



@dp.callback_query_handler(text_startswith="edit_phone1")
async def handler(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer("Введите новый номер телефона: ")
    await D.edit_request_5.set()


@dp.message_handler(state=D.edit_request_5)
async def handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_phone = message.text
    product_id = data["product_id"]
    text = await change_phone(product_id, new_phone)
    await message.answer(text)
    await get_menu(message=message)
    await state.finish()


######################################################################################################


@dp.callback_query_handler(text_startswith="edit_price1")
async def handler(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer("Введите новую цену <b>в цифрах</b>")
    await D.edit_request_4.set()


@dp.message_handler(state=D.edit_request_4)
async def handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_price = message.text
    product_id = data["product_id"]
    text = await change_price(product_id, new_price)
    await message.answer(text)
    await get_menu(message)
    await state.finish()


@dp.callback_query_handler(text_startswith="edit_note1")
async def handler(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer("Введите новое примечание")
    await D.edit_request_3.set()


@dp.message_handler(state=D.edit_request_3)
async def handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_note = message.text
    product_id = data["product_id"]
    text = await change_note(product_id, new_note)
    await message.answer(text)
    await get_menu(message)
    await state.finish()


@dp.callback_query_handler(text_startswith="edit_address1")
async def fdskfj3(call: types.CallbackQuery, state: FSMContext):
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer("Введите новый адрес: ")
    await D.edit_request_2.set()


@dp.message_handler(state=D.edit_request_2)
async def fdf3as(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_address = message.text
    product_id = data["product_id"]
    text = await change_address(product_id, new_address)
    await message.answer(text)
    await get_menu(message)
    await state.finish()


@dp.callback_query_handler(text_startswith="edit_product1", state="*")
async def fdfdsfd13(call: types.CallbackQuery, state: FSMContext):
    prodcut_id = call.data.split(":")[1]
    await state.update_data(product_id=prodcut_id)
    await call.message.answer("Введите новые товары: ")
    await D.edit_request_1.set()


@dp.message_handler(state=D.edit_request_1)
async def fldsk3(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_products = message.text
    product_id = data["product_id"]
    text = await change_product_request(product_id, new_products)
    await message.answer(text)
    await get_menu(message)
    await state.finish()


@dp.message_handler(state=D.edit_product)
async def dasfk12fs21(message: types.Message, state: FSMContext):
    data = message.text
    product = await state.get_data()
    text = await product_edit(product_id=product["product_id"], data=data)
    await message.answer(text)


@dp.message_handler(text="💵 Заработок", state="*")
async def fdsf13fsa(message: types.Message, state: FSMContext):
    await state.finish()
    text = await get_money()
    await message.answer(text)
    await state.finish()
    await cloud()


@dp.message_handler(commands=["backup"], state="*")
async def start(message: types.Message, state: FSMContext):
    await message.reply_document(open("db.sqlite3", "rb"))


@dp.message_handler(text="🎫 Добавить товар", state="*")
async def fdsflj3jf(message: types.Message, state: FSMContext):
    await message.answer(
        "Заполните шаблон и отправьте следующий шаблон боту\n\nТовар\nКоличество (цифрами)\nЦена (цифрами)\nФото (если нет, оставить прочерк - )\n\nЧтобы отменить загрузку товара пропишите /start"
    )
    await cloud()
    await D.dob_tovar.set()


@dp.message_handler(state=D.dob_tovar)
async def fdsfq3xf(message: types.Message, state: FSMContext):
    data = message.text
    text = await add_product_to_db(data)
    await message.answer(text)
    await state.finish()
    await get_menu(message)


@dp.message_handler(text="🛒 Изменить товар")
async def fsfdsjfk23(message: types.Message, state: FSMContext):
    await message.answer("Введит <b>Артикул</b> или <b>Айди</b>")
    await D.change_tovar.set()


@dp.message_handler(state=D.change_tovar)
async def fdslfk32fx(message: types.Message, state: FSMContext):
    nomer_or_pk = message.text
    products = await find_products_tovar(number=nomer_or_pk)
    if products:

        cout_bool = ""
        if products.availability:
            cout_bool = "✅ Есть в наличии"
        else:
            cout_bool = "❌ Нет в наличии ❌"

        text = f"Наличие: <b>{cout_bool}</b>\n \
Товар: <b>{products.product}</b>\n \
Количество: <b>{products.count}</b>\n \
Цена: <b>{products.opt_price}</b>\n \
На сумму: <b>{products.product_suum}</b>\n \
2.5% От Суммы Товара: <b>{products.product_percent}</b>"

        inline_kb_full = types.InlineKeyboardMarkup()
        inline_kb_full.row(
            types.InlineKeyboardButton(
                "Изменить товар", callback_data=f"change_tovar:{products.pk}"
            )
        )
        inline_kb_full.row(
            types.InlineKeyboardButton(
                "Добавить количество", callback_data=f"add_tovar:{products.pk}"
            )
        )
        inline_kb_full.row(
            types.InlineKeyboardButton(
                "Изменить оптовую цену", callback_data=f"change_price_opt:{products.pk}"
            )
        )
        await message.answer(text, reply_markup=inline_kb_full)

    else:
        await message.answer("Товар не найден")
    await state.finish()


@dp.callback_query_handler(text_startswith="change_tovar", state="*")
async def fdsf31fkx1(call: types.CallbackQuery, state: FSMContext):
    await D.tv1.set()
    product_id = call.data.split(":")[1]
    await call.message.answer("✒  Введите новый товар: ")
    await state.update_data(product_id=product_id)


@dp.message_handler(state=D.tv1)
async def fsfdsjfk23(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_product = message.text
    product_id = data["product_id"]
    text = await change_product_tv(
        product_id=product_id, product_product=product_product
    )
    await message.answer(text)
    await state.finish()


@dp.callback_query_handler(text_startswith="add_tovar", state="*")
async def fdsf31fkx1(call: types.CallbackQuery, state: FSMContext):
    await D.tv2.set()
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer(
        "✒  Введите число на котороее надо прибавить количество товара: "
    )


@dp.message_handler(state=D.tv2)
async def handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_count = message.text
    product_id = data["product_id"]
    text = await change_price_tv(product_id=product_id, new_count=new_count)
    await message.answer(text)
    await state.finish()


@dp.callback_query_handler(text_startswith="change_price_opt", state="*")
async def handler(call: types.CallbackQuery, state: FSMContext):
    await D.tv3.set()
    product_id = call.data.split(":")[1]
    await state.update_data(product_id=product_id)
    await call.message.answer("✒  Введите новую цену: ")


@dp.message_handler(state=D.tv3)
async def handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price = message.text
    product_id = data["product_id"]
    text = await сhange_opt(product_id=product_id, price=price)
    await message.answer(text)
    await state.finish()
