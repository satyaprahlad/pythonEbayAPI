import time

import gspread.client
from oauth2client.service_account import ServiceAccountCredentials


class GSheet(object):

    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)

    client = gspread.authorize(creds)


    def updateToGSheet(self,data):

        sheet1 = self.client.open("OrderInformationsWork").worksheet("sheet1")  # Open the spreadhseet
        sheet2 = self.client.open("OrderInformationsWork").worksheet("sheet2")

        data = sheet1.get_all_records()  # Get a list of all records

        row = sheet1.row_values(5)  # Get a specific row
        col = sheet1.col_values(3)  # Get a specific column
        cell = sheet1.cell(2, 1).value  # Get the value of a specific cell
        sheet2.clear()
        insertRow = [cell, "Alexandra", 4, "blue"]

    # sheet.add_rows(insertRow, 4)  # Insert the list as a row at index 4
        sheet2.app
    # sheet2.(2,2, str(datetime.datetime.now()))  # Update one cell
        sheet2.append_rows()

        allRowsValues=list()
        for i in len(data):
            eachItem=data[i]
            eachRow=[eachItem["Title"],  eachItem['SellingStatus']['CurrentPrice']['value'], eachItem['WatchCount'], eachItem['QuantitySold'], eachItem['PrimaryCategory']['CategoryID'],eachItem['ListingDuration']]
            allRowsValues.append(eachRow)

        numRows = sheet1.row_count  # Get the number of rows in the sheet
        sheet2.append_rows(allRowsValues)
        while True:
            break
            sheet1 = gspread.client.open("OrderInformationsWork").worksheet("sheet1")  # Open the spreadhseet
            sheet2 = gspread.client.open("OrderInformationsWork").worksheet("sheet2")

            data = sheet1.get_all_records()  # Get a list of all records

            row = sheet1.row_values(5)  # Get a specific row
            col = sheet1.col_values(3)  # Get a specific column
            cell = sheet1.cell(2,1).value  # Get the value of a specific cell
            sheet2.clear()
            insertRow = [cell, "Alexandra", 4, "blue"]

    #sheet.add_rows(insertRow, 4)  # Insert the list as a row at index 4
