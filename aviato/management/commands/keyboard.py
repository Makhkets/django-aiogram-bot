from aiogram import types

from aviato.models import *

from .config import admins
from .db import *


def admin_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("👤 Сотрудники")
    menu.row("✍ Добавить заявку", "⚒ Браки", "📚 Упакованные") # 📚 Подтвержденные заявки
    menu.row("📕 Отчет", "📔 Заявки")
    menu.row("⚡ Неупокованные заказы", "📢 Логистика")
    menu.row("🚓 Активные заказы водителей", "💵 Заработок", "🌏 Поиск заявок")
    menu.row("💡 Ожидающие чека")
    menu.row("🛒 Изменить товар", "🎫 Добавить товар")
    menu.row("❗ Нет в наличии ❗", "📊 Неотправленные")
    return menu


def manager_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("✍ Добавить заявку", "⚒ Браки")
    menu.row("🌏 Поиск заявок", "📕 Отчет")
    return menu

def operator_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("📔 Заявки", "⚒ Браки")
    menu.row("🌏 Поиск заявок", "📕 Отчет")
    menu.row("💡 Ожидающие чека")
    return menu

def logist_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("📢 Логистика") # 📚 Подтвержденные заявки
    menu.row("🌏 Поиск заявок", "⚒ Браки")
    menu.row("📕 Отчет", "💡 Ожидающие чека")
    return menu

def packer_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("⚡ Неупокованные заказы")
    menu.row("📊 Неотправленные")
    return menu

def supplier_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("🛒 Изменить товар", "🎫 Добавить товар")
    menu.row("✍ Добавить заявку", "💵 Заработок")
    menu.row("❗ Нет в наличии ❗")
    return menu

def driver_menu():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("🚙 Активные заказы", "💡 Ожидающие чека") # Скрытая функция - 🕓 Заказы водителя
    menu.row(types.KeyboardButton("Отправить свою локацию 🗺️", request_location=True))
    return menu

def employees_inline_menu():
    inline_kb_full = types.InlineKeyboardMarkup()
    inline_kb_full.row(types.InlineKeyboardButton("✅ Добавить сотрудника", callback_data="add_employees"))
    inline_kb_full.row(types.InlineKeyboardButton("❌ Изменить должность сотрудника", callback_data="remove_employees"))
    return inline_kb_full

def employees_role_inline():
    inline_kb_full = types.InlineKeyboardMarkup()
    inline_kb_full.row(types.InlineKeyboardButton("🗳️ Логист", callback_data="logist_code"), types.InlineKeyboardButton("👷‍♂️ Снабженец", callback_data="supplier_code"))
    inline_kb_full.row(types.InlineKeyboardButton("🛡️ Админ", callback_data="admin_code"), types.InlineKeyboardButton("⭐ Менеджер", callback_data="manager_code"))
    inline_kb_full.row(types.InlineKeyboardButton("👨‍💻 Оператор", callback_data="operator_code"), types.InlineKeyboardButton("🔧 Водитель", callback_data="driver_code"))
    inline_kb_full.row(types.InlineKeyboardButton("⚙️ Упаковщик", callback_data="packer_code"))
    return inline_kb_full

def question_photo():
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menu.row("✅ Да есть фото", "❌ Фото отсутствует")
    return menu

def get_choice_application():
    inline_kb_full = types.InlineKeyboardMarkup()
    inline_kb_full.row(types.InlineKeyboardButton("🎁 Заявка с Товаром", callback_data="s_product"))
    inline_kb_full.row(types.InlineKeyboardButton("⚠ Заявка без Товара", callback_data="bez_product"))
    return inline_kb_full
