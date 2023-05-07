from __future__ import print_function

import os.path
import time
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .variables import *

def init():
    creds = None
    if os.path.exists('script/token.json'):
        creds = Credentials.from_authorized_user_file('script/token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'script/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('script/token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('sheets', 'v4', credentials=creds)

def convert_phone_number_to_seven(phone):
    dig = r'[\s-]*(\d)' * 6
    for i in re.findall(r'([78])[\s\(]*(\d{3})[\s\)]*(\d)' + dig, phone):
        res = ''.join(i)
        c = res[0].replace("8", "7") + res[1:]
        if c is None:
            return f"Ошибка преобразования номера: ({phone})"
        return c


def getCoordinate(uniqueKey):
    coordinates = []
    sheet = init().spreadsheets()
    for Range in SPREADSHEETS_ID:
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=Range,).execute()
        
        values = result.get('values', [])
        for index, row in enumerate(values):
            try:
                if len(row) >= 14:
                    uniqueKeySheet = row[COLUMN_ID["O"]]
                    if uniqueKey == uniqueKeySheet:
                        print("Нашел координаты:", index + 1)
                        coordinates.append([str(index + 1), Range])

                
            except Exception as e:
                print(f"Error row: {e}")
        time.sleep(1)
    return coordinates

def correct_status(status):
    allstatus = [
        "Ожидает отправки",
        "Неизвестный статус", "Неизвестный статус",
        "Передан логисту", "Передан логисту",
        "Передан диспетчеру", "Передан диспетчеру",
        "Фабричный брак", "Фабричный брак",
        "Дорожный брак", "Дорожный брак",
        "В дороге", "В дороге",
        "Ожидает упаковки", "Ожидает упаковки",
        "Упакован", "Упакован",
        "Ожидание подтверждения", "Ожидание подтверждения",
        "Отменен", "Отменен",
        "Доставлен", "Доставлен",

        # подтверждена
        # упаковано
        # отказ
        # доставлено
    ]

    if status.lower() == "ожидает упаковки" or status.lower() == "подтверждена": return "Подтверждена"
    if status.lower() == "упакован" or status.lower() == "упаковано": return "Упаковано"
    if status.lower() == "ожидание подтверждения" or status.lower() == "обрабатывается": return "Обрабатывается"
    if status.lower() == "отменен" or status.lower() == "отказ": return "Отказ"
    if status.lower() == "доставлен" or status.lower() == "доставлено": return "Доставлено"
    
    if status in allstatus:
        return status

    return "Неизвестный статус"

def getWriteInfo(data, symbol):
    if "C" == symbol:
        return data.address.split("г.")[1].split("\n")[0]
    elif "D" == symbol:
        return data.product
    elif "E" == symbol:
        return convert_phone_number_to_seven(data.phone)
    elif "F" == symbol:
        return data.price
    elif "H" == symbol:
        return correct_status(data.status)
    elif "J" == symbol: # Примечание``
        address = data.address.split('\n')[1]
        return f"{address} \
            \n\n{convert_phone_number_to_seven(data.phone)} \
            \n\n{data.product} \
            \n\n{data.note} \
            \n\nИтоговая: {data.price}"


def updateSheet(coordinates, data):
    # C-city, D-product, E-phone, F-price, H-status
    symbols = ["C", "D", "E", "F", "H", "J"]
    sheet = init().spreadsheets()
    for coordinate in coordinates:
        for symbol in symbols:
            range_name = f"{coordinate[1]}!{symbol}{coordinate[0]}"
            sheet.values().update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body={"values": [[getWriteInfo(data, symbol)]]}
            ).execute()
            time.sleep(1)

def append_to_sheet(data):
    # C-city, D-product, E-phone, F-price, H-status
    symbols = ["C", "D", "E", "F", "H", "J"]
    sheet = init().spreadsheets()
    range_ = f'Заявки!C:J'

    # Данные, которые следует добавить в новую строку
    # new_row = [data.address, data.product, data.phone, data.price, "", correct_status(data.status)]

    # Получение всех значений из листа
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_).execute()

    # Определение индекса последней строки \ получаем следующую строку
    last_row_index = len(result.get('values', [])) + 1


    for symbol in symbols:
        time.sleep(1)
        range_name = f"Заявки!{symbol}{last_row_index}"
        sheet.values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={"values": [[getWriteInfo(data, symbol)]]}
        ).execute()
        

    print("Загрузил новую строку в google sheets")

    return last_row_index

def delete_sheet_information(data):
    sheet_info = getCoordinate(data.uniqueKey)
    coordinate = sheet_info[0][0]
    current_sheet = sheet_info[0][1]

    print("Координаты удаления:", coordinate)
    print("Лист:", current_sheet)

    sheet = init().spreadsheets()
    symbols = ["C", "D", "E", "F", "H", "J"]
    for symbol in symbols:
        range_name = f"{current_sheet}!{symbol}{coordinate}"
        sheet.values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={"values": [[""]]}
        ).execute()
        time.sleep(1)