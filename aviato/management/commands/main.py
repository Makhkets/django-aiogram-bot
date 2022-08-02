
import logging
import datetime
from random import randint

from aiogram import Bot, Dispatcher, executor, types
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
	address = State()
	prod = State()

	match = State()
	match2 = State()

	match3 = State()
	match4 = State()

	remake_request = State()
	edit_product = State()

async def get_menu(message):
	user = await get_user_or_create(user_id=str(message.from_user.id), username=message.from_user.username)

	if message.chat.id in admins:
		await message.answer(f'{message.from_user.first_name} 👋. \n\n(У вас роль Администратора)', reply_markup=admin_menu())
	
	elif user.role == "Админ":
		await message.answer(f'{message.from_user.first_name} 👋. \n\n(У вас роль Администратора)', reply_markup=admin_menu())

	elif user.role == "Менеджер":
		await message.answer(f'{message.from_user.first_name} 👋. \n\n(У вас роль Менеджера)', reply_markup=manager_menu())

	elif user.role == "Оператор":
		await message.answer(f'{message.from_user.first_name} 👋. \n\n(У вас роль Оператора)', reply_markup=operator_menu())

	elif user.role == "Логист":
		await message.answer(f'{message.from_user.first_name} 👋. \n\n(У вас роль Логиста)', reply_markup=logist_menu())

	elif user.role == "Упаковщик":
		await message.answer(f'{message.from_user.first_name} 👋. \n\n(У вас роль Упаковщика)', reply_markup=packer_menu())

	elif user.role == "Водитель":
		await message.answer(f'{message.from_user.first_name} 👋. \n\n(У вас роль Водитель)', reply_markup=driver_menu())

	else:
		await message.answer(f'{message.from_user.first_name} 👋, \n\nу вас нет роли, напишите команду /code и введите код')

async def get_menu_call(call):
	user = await get_user_or_create(user_id=str(call.message.chat.id), username=call.message.from_user.username)
	if call.message.chat.id in admins:
		await call.message.answer(f'🔙 Вы перемещены в главное меню', reply_markup=admin_menu())

	elif user.role == "Админ":
		await call.message.answer(f'🔙 Вы перемещены в главное меню', reply_markup=admin_menu())
	
	elif user.role == "Менеджер":
		await call.message.answer(f'🔙 Вы перемещены в главное меню', reply_markup=manager_menu())

	elif user.role == "Оператор":
		await call.message.answer(f'🔙 Вы перемещены в главное меню', reply_markup=operator_menu())

	elif user.role == "Логист":
		await call.message.answer(f'🔙 Вы перемещены в главное меню', reply_markup=logist_menu())

	elif user.role == "Упаковщик":
		await call.message.answer(f'🔙 Вы перемещены в главное меню', reply_markup=packer_menu())

	elif user.role == "Водитель":
		await call.message.answer(f'🔙 Вы перемещены в главное меню', reply_markup=driver_menu())


async def cloud():
	products = await drive_products()
	for product in products:
		time = int(str(product.time_update_location).split(" ")[1].split(":")[0])
		current_time = int(str(datetime.datetime.now()).split(" ")[1].split(":")[0])
		every_hours = current_time - time - 3
		if every_hours > 6:
			if product.status == "В дороге":
				await bot.send_message(product.user.user_id, "❗ Обновите свою геолокацию") 
		if every_hours > 20:
			if product.status == "Ожидание подтверждения":
				operators = await get_operators()
				for operator in operators:
					await bot.send_message(operator.user_id, "❗ У вас есть необработанныее заказы")
			elif product.status == "Подтвержден":
				logists = await get_operators()
				for logist in logists:
					await bot.send_message(logist.user_id, "❗ У вас есть необработанныее заказы")



	

@dp.message_handler(commands=['start'], state="*")
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
	await call.message.answer("Выберите роль будущего сотрудника:", reply_markup=employees_role_inline())
	await cloud()

@dp.callback_query_handler(text_startswith="admin_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
	code = randint(100, 999)
	await create_code_employees(user_id=call.message.chat.id, code=code, role="Админ")
	await get_menu_call(call)
	await call.message.answer(f"Код чтобы получить статус <b>Админа</b> в боте\n\nКод: <code>{code}</code>")
	await cloud()

@dp.callback_query_handler(text_startswith="manager_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
	code = code = randint(100, 999)
	await create_code_employees(user_id=call.message.chat.id, code=code, role="Менеджер")
	await get_menu_call(call)
	await call.message.answer(f"Код чтобы получить статус <b>Менеджера</b> в боте\n\nКод: <code>{code}</code>")
	await cloud()

@dp.callback_query_handler(text_startswith="operator_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
	code = code = randint(100, 999)
	await create_code_employees(user_id=call.message.chat.id, code=code, role="Оператор")
	await get_menu_call(call)
	await call.message.answer(f"Код чтобы получить статус <b>Оператора</b> в боте\n\nКод: <code>{code}</code>")
	await cloud()

@dp.callback_query_handler(text_startswith="driver_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
	code = code = randint(100, 999)
	await create_code_employees(user_id=call.message.chat.id, code=code, role="Водитель")
	await get_menu_call(call)
	await call.message.answer(f"Код чтобы получить статус <b>Водителя</b> в боте\n\nКод: <code>{code}</code>")
	await cloud()

@dp.callback_query_handler(text_startswith="packer_code", state="*")
async def dsa1rfxsf3(call: types.CallbackQuery, state: FSMContext):
	code = code = randint(100, 999)
	await create_code_employees(user_id=call.message.chat.id, code=code, role="Упаковщик")
	await get_menu_call(call)
	await call.message.answer(f"Код чтобы получить статус <b>Упаковщик</b> в боте\n\nКод: <code>{code}</code>")
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
			inlineh1.row(types.InlineKeyboardButton("Админ", callback_data=f"remove_admin:{user.user_id}"), types.InlineKeyboardButton("Менеджер", callback_data=f"remove_manager:{user.user_id}"))
			inlineh1.row(types.InlineKeyboardButton("Оператор", callback_data=f"remove_operator:{user.user_id}"), types.InlineKeyboardButton("Водитель", callback_data=f"remove_driver:{user.user_id}"))
			inlineh1.row(types.InlineKeyboardButton("Упаковщик", callback_data=f"remove_packer:{user.user_id}"))
			await message.answer(f"Имя: @{user.username}\nID: {user.user_id}\nРоль: {user.role}\n\nВыберите роль для пользователя", reply_markup=inlineh1)
	else: await message.answer("❌ Неравильно введен ID")
	await state.finish()
	await cloud()

@dp.callback_query_handler(text_startswith="remove_admin", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	user_id = call.data.split(":")[1]
	user = await change_role_user(user_id=str(user_id), role="Админ")
	await get_menu_call(call)
	await call.message.answer("✅ Успешно поменял роль сотрудника на роль: <b>Админа</b>")
	await cloud()

@dp.callback_query_handler(text_startswith="remove_manager", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	user_id = call.data.split(":")[1]
	user = await change_role_user(user_id=str(user_id), role="Менеджер")

	await get_menu_call(call)
	await call.message.answer("✅ Успешно поменял роль сотрудника на роль: <b>Менеджера</b>")
	await cloud()

@dp.callback_query_handler(text_startswith="remove_operator", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	user_id = call.data.split(":")[1]
	user = await change_role_user(user_id=str(user_id), role="Менеджер")

	await get_menu_call(call)

	await call.message.answer("✅ Успешно поменял роль сотрудника на роль: <b>Оператора</b>")
	await cloud()

@dp.callback_query_handler(text_startswith="remove_driver", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	user_id = call.data.split(":")[1]
	user = await change_role_user(user_id=str(user_id), role="Водитель")
	await get_menu_call(call)
	await call.message.answer("✅ Успешно поменял роль сотрудника на роль: <b>Водителя</b>")
	await cloud()

@dp.callback_query_handler(text_startswith="remove_packer", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	user_id = call.data.split(":")[1]
	user = await change_role_user(user_id=str(user_id), role="Упаковщик")
	await get_menu_call(call)
	await call.message.answer("✅ Успешно поменял роль сотрудника на роль: <b>Упаковщика</b>")
	await cloud()

@dp.message_handler(commands=['code'], state="*")
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
	name = f'{message.text}'
	await change_name(user_id=str(message.from_user.id), name=name)
	await message.answer("Успешно добавил вас в базу.")
	await state.finish()
	await get_menu(message)
	await cloud()

@dp.message_handler(text="✍ Добавить заявку", state="*")
async def userrequests(message: types.Message):
	await message.answer("🖋 Заполните и отправьте следующий шаблон\n\nПримечание\nТовар\nАдрес\nНомер\nЦена\nФото\n\nЧтобы отменить загрузку товара напишите /start")
	await D.note.set()
	await cloud()

@dp.message_handler(state=D.note)
async def userrequests(message: types.Message, state: FSMContext):
	data = message.text.split("\n")
	text = await product_save(user_id=str(message.from_user.id), data=data)
	await message.answer(text)
	await state.finish()
	await cloud()

@dp.message_handler(text="📔 Заявки", state="*")
async def employees(message: types.Message):
	products = await get_confirm_products()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("❌ Отменить заявку", callback_data=f"remove_request:{product.pk}"))
			inlineh1.row(types.InlineKeyboardButton("✅ Подтвердить заявку", callback_data=f"confirm_request:{product.pk}"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("Пока нет заявок.")
	await cloud()

@dp.message_handler(text="📔 Все Заявки", state="*")
async def employees(message: types.Message):
	products = await get_products()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("❌ Удалить заявку", callback_data=f"remove_request:{product.pk}"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("Пока нет заявок.")
	await cloud()

@dp.callback_query_handler(text_startswith="confirm_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	text = await confirm_product(product_id=product_id)
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

@dp.message_handler(text="📕 Отчет", state="*")
async def employees(message: types.Message):
	answer = await report_info()
	user = await get_user_or_create(user_id=str(message.from_user.id))

	inlineh1 = types.InlineKeyboardMarkup()
	inlineh1.row(types.InlineKeyboardButton("Ожидающие подтверждения", callback_data="ojid_confirmed"))
	inlineh1.row(types.InlineKeyboardButton("Подтвержденные", callback_data="oj_confirmd"), types.InlineKeyboardButton("Отмененные", callback_data="oj_canceled"))
	inlineh1.row(types.InlineKeyboardButton("Переданные Упаковщику", callback_data="oj_packer"))
	inlineh1.row(types.InlineKeyboardButton("Переданные диспетчеру", callback_data="oj_dispatcher"), types.InlineKeyboardButton("В дороге", callback_data="oj_drive"))
	inlineh1.row(types.InlineKeyboardButton("Дорожный брак", callback_data="oj_dorozh_brak"), types.InlineKeyboardButton("Фабричный брак", callback_data="oj_fabr_brak"))
	inlineh1.row(types.InlineKeyboardButton("Доставлено", callback_data="oj_delevired"))

	await message.answer(answer, reply_markup=inlineh1)
	await cloud()


# Доставлено
@dp.callback_query_handler(text_startswith="oj_delevired", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await oj_delivered()
	products1 = await dorozh_brak_products()
	products2 = await fabr_brack_products()

	if len(products) >= 1:
		for product in products2:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: pass

	if len(products) >= 1:
		for product in products1:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: pass

	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: pass




# Фабричный брак
@dp.callback_query_handler(text_startswith="oj_fabr_brak", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await fabr_brack_products()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: await call.message.answer("❌ Ничего не найдено")

# Дорожный брак
@dp.callback_query_handler(text_startswith="oj_dorozh_brak", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await dorozh_brak_products()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: await call.message.answer("❌ Ничего не найдено")

# В дороге
@dp.callback_query_handler(text_startswith="oj_drive", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await get_drive_pr()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: await call.message.answer("❌ Ничего не найдено")

# Переданные диспетчеру
@dp.callback_query_handler(text_startswith="oj_dispatcher", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await get_dispatchers()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: await call.message.answer("❌ Ничего не найдено")

# Переданные Упаковщику
@dp.callback_query_handler(text_startswith="oj_packer", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await get_packers()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: await call.message.answer("❌ Ничего не найдено")

# Отмененные
@dp.callback_query_handler(text_startswith="oj_canceled", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await get_canceled()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: await call.message.answer("❌ Ничего не найдено")

# Подтвержденные
@dp.callback_query_handler(text_startswith="oj_confirmd", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await get_confirmed()
	l.success(products)
	if products is None:
		await call.message.answer("❌ Ничего не найдено")
	else:
		if len(products) >= 1:
			for product in products:
				text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
				inlineh1 = types.InlineKeyboardMarkup()
				inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
				if "http://" in str(product.photo) or "https://" in str(product.photo):
					await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
				elif "media/users/" in str(product.photo):
					await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
				else:
					await call.message.answer(text, reply_markup=inlineh1)
		else: await call.message.answer("❌ Ничего не найдено")

# Ожидающие подтверждения
@dp.callback_query_handler(text_startswith="ojid_confirmed", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	products = await get_ojid_confirmed()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("Скрыть", callback_data=f"message_hide"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await call.message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await call.message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await call.message.answer(text, reply_markup=inlineh1)
	else: await call.message.answer("❌ Ничего не найдено")



@dp.message_handler(text="📚 Подтвержденные заявки", state="*")
async def employees(message: types.Message):
	products = await get_confirmed_products()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("✅ Отправить товар на упаковку", callback_data=f"confirmed_request:{product.pk}"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("Пока нет подтвержденных заявок.")
	await cloud()

@dp.callback_query_handler(text_startswith="confirmed_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	text = await product_pack(product_id=product_id)
	await get_menu_call(call)
	await call.message.answer(text)
	await cloud()

@dp.message_handler(text="⚡ Неупокованные заказы", state="*")
async def employees(message: types.Message):
	products = await get_pack_products()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("✅ Заказ упакован", callback_data=f"confirmed2_request:{product.pk}"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("Пока нет заявок для упаковки.")
	await cloud()

@dp.callback_query_handler(text_startswith="confirmed2_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	text = await product_pack_conf(product_id=product_id)
	await get_menu_call(call)
	await call.message.answer(text)
	await cloud()

@dp.callback_query_handler(text_startswith="confirmed_drive_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	text = await handover_product_to_drive(product_id=product_id, user_id=str(call.message.chat.id))
	await get_menu_call(call)
	await call.message.answer(text)
	await cloud()

@dp.message_handler(text="🚙 Активные заказы", state="*")
async def employees(message: types.Message):
	products = await get_active_requests_drive(user_id=message.from_user.id)

	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("✅ Я доставил этот заказ", callback_data=f"conf_r_request:{product.pk}"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("У вас нет активных заявок на доставку.")
	await cloud()

@dp.callback_query_handler(text_startswith="conf_r_request", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	text = await delivered(product_id=product_id)
	await get_menu_call(call)
	await call.message.answer(text)
	await cloud()

@dp.message_handler(content_types=['location'])
async def employees(message: types.Message):
	latitude = message.location["latitude"]
	longitude = message.location["longitude"]

	ua = UserAgent()
	random_user_agent = ua.random
	locator = Nominatim(user_agent=random_user_agent)
	address = locator.reverse(f'{latitude}, {longitude}')

	admin_list = await admins_list()
	for admin in admin_list:
		await bot.send_message(admin.user_id, "✅ Водитель обновил свою геолокацию")

	text = address.address
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
			inlineh1.row(types.InlineKeyboardButton("🗺 Получить геолокацию", callback_data=f"location_dr:{product.pk}"))
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("❌ Товары отсутствуют")
	await cloud()

@dp.callback_query_handler(text_startswith="location_dr", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	product = await plea_location(product_id=product_id)
	await bot.send_message(product.driver.user_id, "<b>❗❗ Администратор просит вас отправить вашу геолокацию нажав на кнопку \"Отправить свою локацию 🗺️\"</b>")
	await call.message.answer("✅ Отправил запрос на получение геолокации водителя")
	await cloud()

@dp.message_handler(commands=['product'], state="*")
async def start(message: types.Message, state: FSMContext):
	await message.answer("🆔 Введите ID товара: ")
	await D.prod.set()
	await cloud()

@dp.message_handler(state=D.prod)
async def employees(message: types.Message, state: FSMContext):
	product_id = message.text
	product = await find_product(product_id=product_id)
	inlineh1 = types.InlineKeyboardMarkup()
	inlineh1.row(types.InlineKeyboardButton("🗺 Получить геолокацию", callback_data=f"location_dr:{product.pk}"))
	
	
	if product.status == "Доставлен" or "В дороге" == product.status:
		text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}\nСтатус заявки: {product.status}"
	else: text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nЗагрузил товар: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}\nСтатус заявки: Подготавливается к отправке"

	await message.answer(text, reply_markup=inlineh1)
	await cloud()

@dp.message_handler(text="🕓 Заказы водителя", state="*")
async def employees(message: types.Message):
	products = await pack_to_drive()
	if len(products) >= 1:
		for product in products:
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton("✅ Принять заказ на доставку", callback_data=f"confirmed_drive_request:{product.pk}"))
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("Пока нет упакованных заявок.")
	await cloud()

@dp.message_handler(text="📢 Логистика", state="*")
async def employees(message: types.Message):
	products = await pack_to_logist()
	if len(products) >= 1:
		for product in products:
			
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"

			drivers = await get_all_drivers()
			inlineh1 = types.InlineKeyboardMarkup()
			
			if drivers.count() > 0:
				for driver in drivers:
					inlineh1.row(types.InlineKeyboardButton(f"🚗 {driver.first_name}", callback_data=f"driv:{driver.pk}:{product.pk}"))
			else: inlineh1.row(types.InlineKeyboardButton(f"❌ Водители отсутствуют", callback_data=f"dsdsdriv"))
				
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	else: await message.answer("Пока нет упакованных заявок.")
	await cloud()


@dp.callback_query_handler(text_startswith="driv", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	user_id = call.data.split(":")[1]
	product_id = call.data.split(":")[2]

	product = await get_product(product_id=product_id)
	user = await get_user(user_id=str(user_id))
	user_id = user.user_id

	if product:
		text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
		inlineh1 = types.InlineKeyboardMarkup()
		inlineh1.row(types.InlineKeyboardButton(f"✅ Принять заказ", callback_data=f"dr_confirmed:{user_id}:{product_id}"))
			
		if "http://" in str(product.photo) or "https://" in str(product.photo):
			await bot.send_photo(chat_id=user_id, photo=str(product.photo), caption=text, reply_markup=inlineh1)
		elif "media/users/" in str(product.photo):
			await bot.send_photo(chat_id=user_id, photo=open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
		else:
			await bot.send_message(chat_id=user_id, text=text, reply_markup=inlineh1)
		await call.message.delete()
		await call.message.answer("✅ Успешно")
	else: await call.message.answer("❌ Такой товар уже не существуют, возможно его кто то удалил")
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
			inlineh1.row(types.InlineKeyboardButton(f"Фабричный брак", callback_data=f"product_brak_f:{product.pk}"),
						 types.InlineKeyboardButton(f"Дорожный брак", callback_data=f"product_brak_d:{product.pk}"))
			inlineh1.row(types.InlineKeyboardButton(f"Скрыть", callback_data="message_hide"))

			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			if "http://" in str(product.photo) or "https://" in str(product.photo):
				await message.answer_photo(str(product.photo), caption=text, reply_markup=inlineh1)
			elif "media/users/" in str(product.photo):
				await message.answer_photo(open(str(product.photo), 'rb'), caption=text, reply_markup=inlineh1)
			else:
				await message.answer(text, reply_markup=inlineh1)
	except Exception as ex: await message.answer(f"❌ Товар не найден ({ex})")
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
	await call.message.answer("Отправьте сообщениее по следующему шаблону\n\nТовар\nНовая цена")
	await cloud()

@dp.message_handler(state=D.match3)
async def employees(message: types.Message, state: FSMContext):
	_ = await state.get_data()
	data = message.text.split("\n")

	product_title = data[0]
	product_price = data[1]
	product_id = _["product_id"]

	text = await product_match(title=product_title, price=product_price, product_id=product_id, status="Дорожный брак")
	await message.answer(text)
	await state.finish()
	await get_menu(message)
	await cloud()



@dp.callback_query_handler(text_startswith="product_brak_f", state="*")
async def add_employeees(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	await D.match2.set()
	await state.update_data(product_id=product_id)
	await call.message.answer("Отправьте сообщениее по следующему шаблону\n\nТовар\nНовая цена")
	await cloud()

@dp.message_handler(state=D.match2)
async def employees(message: types.Message, state: FSMContext):
	_ = await state.get_data()
	data = message.text.split("\n")

	product_title = data[0]
	product_price = data[1]
	product_id = _["product_id"]

	text = await product_match(title=product_title, price=product_price, product_id=product_id, status="Фабричный брак")
	await message.answer(text)
	await state.finish()
	await get_menu(message)
	await cloud()



@dp.message_handler(text="🌏 Редактировать заявку", state="*")
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
	else:
		for product in products:
			inlineh1 = types.InlineKeyboardMarkup()
			inlineh1.row(types.InlineKeyboardButton(f"🖋 Редактировать заявку", callback_data=f"edit_request:{product.pk}"))
			inlineh1.row(types.InlineKeyboardButton(f"♻ Скрыть заявку", callback_data=f"hide_message"))
			text = f"Примечание: {product.note}\nАдресс: {product.address}\nТовар: {product.product}\nЦена: {product.price}\nНомер: {product.phone}\nВладелец товара: @{product.user.username} ({product.user.role})\n\nID: {product.pk}\nЛокация водителя: {str(product.location).replace('None', 'Водитель пока что не оставил свою геолокацию')}\nИзменение локации было в: {str(product.time_update_location).split('.')[0]}"
			await message.answer(text, reply_markup=inlineh1)

@dp.callback_query_handler(text_startswith="hide_message", state="*")
async def fdfdsfd13(call: types.CallbackQuery, state: FSMContext):
	await call.message.delete()
	await call.message.answer("✅ Успешно")


@dp.callback_query_handler(text_startswith="edit_request", state="*")
async def fdsf31fkx1(call: types.CallbackQuery, state: FSMContext):
	product_id = call.data.split(":")[1]
	await state.update_data(product_id=product_id)
	await call.message.answer("Заполните следующий шаблон:\n\n🖋 Заполните и отправьте следующий шаблон\n\nПримечание\nАдрес\nТовар\nЦена\nНомер\nФото\n\nЧтобы отменить загрузку товара напишите /start")
	await D.edit_product.set()

@dp.message_handler(state=D.edit_product)
async def dasfk12fs21(message: types.Message, state: FSMContext):
	data = message.text
	product = await state.get_data()
	text = await product_edit(product_id=product['product_id'], data=data)
	await message.answer(text)


@dp.message_handler(text="💵 Заработок", state="*")
async def fdsf13fsa(message: types.Message, state: FSMContext):
	text = await get_money()
	await message.answer(text)
	await state.finish()
	await cloud()












