import random
import traceback

from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping

import datetime
import time
import gspread.client
from oauth2client.service_account import ServiceAccountCredentials


# scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
#              "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
#
# creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)
#
# client = gspread.authorize(creds)
#
# sheet1 = client.open("OrderInformationsWork").worksheet("Input")
# sheet1.update_cell(4,2,"")
# sheet1.format("B4:B4", {"backgroundColor": {
#     "red": 1.0,
#     "green": 0.8,
#     "blue": 0.3
#  },"textFormat": {"bold": False, "fontSize": 12, }})
#
#
# ages = {'Jim': 30, 'Pam': 28, 'Kevin': 33}
# person = input('Get age for: ')
# age = ages.get(person)
# if age is None:
#     print("none")
#     print(ages[person])
import traceback

try:
    1/0
except Exception as err:
    print(err)
    traceback.print_exc()