from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1LkNP8mSz3cyOCOF-JnW24YMsjXu_fEIG3nlmm54Bnq8'
SPREADSHEETS_ID = {
    "Заявки": "!A2:T",
    "Не отпр": "!A2:T",
    "Ждут отпр.": "!A2:T",
    "Отпр. ДСП": "!A2:T",
}

COLUMN_ID = {
    "A": 0,  # Дата
    "B": 1,  # ДСП
    "C": 2,  # Город
    "D": 3,  # Товар
    "E": 4,  # Телефон
    "F": 5,  # Цена
    "G": 6,  # 
    "H": 7,  # Статус
    "I": 8,  # У кого
    "J": 9,  # В дороге
    "K": 10, #  
    "L": 11, # 
    "M": 12, # 
    "O": 14, # Номер заказа
}


import os
import sys
import time
import django

parent_dir = os.path.abspath(os.path.dirname(__file__)).replace(os.path.abspath(os.path.dirname(__file__)).split("\\", -1)[-1], "")

sys.path.append(parent_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from aviato.models import Applications



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

def get_status(status: str):
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

    if status.lower() == "ожидает упаковки" or status.lower() == "подтверждена": return "Ожидает упаковки"
    if status.lower() == "упакован" or status.lower() == "упаковано": return "Упакован"
    if status.lower() == "ожидание подтверждения" or status.lower() == "обрабатывается": return "Ожидание подтверждения"
    if status.lower() == "отменен" or status.lower() == "отказ": return "Отменен"
    if status.lower() == "доставлен" or status.lower() == "доставлено": return "Доставлен"
    
    if status in allstatus:
        return status

    return "Неизвестный статус"

def main():
    sheet = init().spreadsheets()
    for Range in SPREADSHEETS_ID:
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=Range,).execute()
        
        
        values = result.get('values', [])
        for _, row in enumerate(values):
            try:
                city = row[COLUMN_ID["C"]]
                product = row[COLUMN_ID["D"]]
                phone = row[COLUMN_ID["E"]]
                price = row[COLUMN_ID["F"]]
                status = row[COLUMN_ID["H"]]
                
                note = row[COLUMN_ID["J"]]

                uniqueKey = row[COLUMN_ID["O"]]

                if uniqueKey.isdigit():
                    if product != "":
                        a = Applications.objects.get(uniqueKey=uniqueKey)
                        if product != a.product or phone != a.phone or price != a.price or \
                            get_status(status) != get_status(a.status) or \
                                  a.address != city or a.note != note:
                        
                            a.product = product
                            a.phone = phone
                            a.price = price
                            a.status = get_status(status)
                            a.address = city
                            a.note = note
                            a.save(perform_logic=True)
                            print("Нашел и изменил заявку")


            except Applications.DoesNotExist:
                Applications.create(
                    product=product,
                    phone=phone,
                    price=price,
                    status=get_status(status),
                    address=city,
                    note=note,
                    uniqueKey=uniqueKey,
                    perform_logic=True,
                ); print("Добавил новую заявку1")

            except IndexError: pass
            except Exception as e:
                print(f"Error row: {e}")

        

while 1:
    main()
    time.sleep(300)
    

                # row_number = index + 1
                # range_name = f"Заявки!P{row_number}"
                # sheet.values().update(
                #     spreadsheetId=SAMPLE_SPREADSHEET_ID,
                #     range=range_name,
                #     valueInputOption="USER_ENTERED",
                #     body={"values": [["TEST"]]}
                # ).execute()