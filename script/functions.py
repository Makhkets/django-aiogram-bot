from __future__ import print_function

import os.path

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
        return data.address
    elif "D" == symbol:
        return data.product
    elif "E" == symbol:
        return data.phone
    elif "F" == symbol:
        return data.price
    elif "H" == symbol:
        return correct_status(data.status)
    elif "J" == symbol:
        return data.note
    

def  updateSheet(coordinates, data):
    # C-city, D-product, E-phone, F-price, H-status
    symbols = ["C", "D", "E", "F", "H", "J"]
    for coordinate in coordinates:
        sheet = init().spreadsheets()

        for symbol in symbols:
            range_name = f"{coordinate[1]}!{symbol}{coordinate[0]}"
            sheet.values().update(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body={"values": [[getWriteInfo(data, symbol)]]}
            ).execute()

def append_to_sheet(data):
    # C-city, D-product, E-phone, F-price, H-status
    symbols = ["C", "D", "E", "F", "H"]
    sheet = init().spreadsheets()
    range_ = f'Заявки!C:J'

    # Данные, которые следует добавить в новую строку
    # new_row = [data.address, data.product, data.phone, data.price, "", correct_status(data.status)]

    # Получение всех значений из листа
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=range_).execute()

    # Определение индекса последней строки \ получаем следующую строку
    last_row_index = len(result.get('values', [])) + 1


    for symbol in symbols:
        range_name = f"Заявки!{symbol}{last_row_index}"
        sheet.values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body={"values": [[getWriteInfo(data, symbol)]]}
        ).execute()

    print("Загрузил новую строку в google sheets")