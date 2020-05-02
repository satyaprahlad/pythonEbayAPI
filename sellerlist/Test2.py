import traceback

from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping

import datetime
import time
import gspread.client
from oauth2client.service_account import ServiceAccountCredentials


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)

client = gspread.authorize(creds)

sheet1 = client.open("OrderInformationsWork").worksheet("Input")
print(sheet1.cell(4,2).value)