from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from aviato.models import Applications

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID = '1LkNP8mSz3cyOCOF-JnW24YMsjXu_fEIG3nlmm54Bnq8'
# SAMPLE_RANGE_NAME = 'Заявки!A2:E'
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


def init():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('sheets', 'v4', credentials=creds)



def main():
    my_objects = Applications.objects.all()
    for obj in my_objects:
        print(obj.field_name)
    
    
    # sheet = init().spreadsheets()
    # for Range in SPREADSHEETS_ID:
    #     result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                                 range=Range,).execute()
        
        
    #     values = result.get('values', [])
    #     for index, row in enumerate(values):
    #         try:

    #             print(row)

    #             # row_number = index + 1
    #             # range_name = f"Заявки!P{row_number}"
    #             # sheet.values().update(
    #             #     spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #             #     range=range_name,
    #             #     valueInputOption="USER_ENTERED",
    #             #     body={"values": [["TEST"]]}
    #             # ).execute()

                 
    #             break
    #         except Exception as e:
    #             print(f"Error updating row: {e}")
        
    #     break

main()