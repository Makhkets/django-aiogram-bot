from pprint import pprint
from openpyxl import load_workbook
import requests
from bs4 import BeautifulSoup
from loguru import logger as l

p = load_workbook(filename="products.xlsx")
worksheet = p.active

PRODUCTS = []

add_url = "http://127.0.0.1:8000/admin/aviato/products/add/"

for i in range(2, 64):
    PRODUCTS.append(
        (
            (worksheet["A" + str(i)].value),
            (worksheet["B" + str(i)].value),
            (worksheet["C" + str(i)].value),
        )
    )
    


for product in PRODUCTS:
    soup = BeautifulSoup(requests.get(add_url, headers={
        "Cookie": "_ym_d=1658843588; _ym_uid=1658843588915356249; _ga=GA1.1.1519580526.1658843588; _ga_6ZLVWWERXG=GS1.1.1658864157.1.1.1658864191.0; SL_G_WPT_TO=ru; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; csrftoken=Vn8PiuT2wIfXmmjL8LZVn9aIn8Qmi8G48QSYH5srdVquNUSv8BwJtLUB5lWPtQw4; sessionid=kiw7qwdudhg266mx0f45pzaomahdxwk1"
    }).text, "lxml")
    token = soup.find("input", {"name": "csrfmiddlewaretoken"}).get("value")
    # l.success(token)
    r = requests.post("http://127.0.0.1:8000/admin/aviato/products/add/", data={
        "csrfmiddlewaretoken": token,
        "product": product[0],
        "count": product[1],
        "opt_price": product[2],
        "photo": "",
        "availability": "on",
        "_save": "Сохранить",
    }, headers={
        "Cookie": "_ym_d=1658843588; _ym_uid=1658843588915356249; _ga=GA1.1.1519580526.1658843588; _ga_6ZLVWWERXG=GS1.1.1658864157.1.1.1658864191.0; SL_G_WPT_TO=ru; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; csrftoken=Vn8PiuT2wIfXmmjL8LZVn9aIn8Qmi8G48QSYH5srdVquNUSv8BwJtLUB5lWPtQw4; sessionid=kiw7qwdudhg266mx0f45pzaomahdxwk1"
    })
    l.success(token)