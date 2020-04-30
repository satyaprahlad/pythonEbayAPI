from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
import json
import datetime
import time
import gspread.client
from oauth2client.service_account import ServiceAccountCredentials


def updateToGSheet( data):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)

    client = gspread.authorize(creds)

    sheet1 = client.open("OrderInformationsWork").worksheet("sheet1")

    eachRow = ['Title', 'Price', 'Watch',
               'Sold', 'CategoryID',
               'Duration']
    #heading

    sheet1.clear()
    sheet1.append_row(eachRow)
    allRowsValues = list()
    for i in range(len(data)):

        eachItem = data[i]
        print(eachItem)
        eachRow = [eachItem['Title'], float(eachItem['SellingStatus']['CurrentPrice']['value']), int(eachItem['WatchCount']),
                   int(eachItem['SellingStatus']['QuantitySold']), int(eachItem['PrimaryCategory']['CategoryID']), eachItem['ListingDuration']]
        allRowsValues.append(eachRow)

    #print("all rows are ",allRowsValues)

    sheet1.append_rows(allRowsValues)
    sheet1.format("A1:F1", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 1.0,
        "green": 0.0,
        "blue": 0.0
    }}})

def main():

    api = Trading(config_file=None,domain='api.ebay.com',appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe", devid="6c042b69-e90f-4897-9045-060858248665",
              certid="AgAAAA**AQAAAA**aAAAAA**zY2pXg**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6MElIuoC5CEpAydj6x9nY+seQ**/0kGAA**AAMAAA**7/kuig0GXA6zyrQ/D6lHcXQVtH2z/rLeU4EzvA4jqRnDtBEXlUMdK5ZuE0EpkrfiI7bUcY6xVnn9C/6Iajfk9uhKoayDerpacV7wwRbELehUna4jXa57klixCENuF6UbPprzmnbIVt0pdoWNw5Yfa9dSEZb6FKw4eVwWwwABNUOIxd7ozBMVoZwywBQ5JwOKl2U8wzfnxzNH/tiSn5NSkiqOJztVlOT5XZWPB1wlaoZsLrGBxZDEeAQ3C+fKOm5NJIpEn6YCZF7u0SPulv2I4gcXCJVUQ8en7bClXajs4c/Qfo+gelpYHKKeTWVInQbqcEF+OoUcA0deqjYgIxsJ6J0iRXQoaESYV1tZ1zLVvNcxrysuwVpV7Iwjs5alfKQmAgVlBFjstbi3Pgr/NFR3s3srGR6DLoBNfF6w2yP6LE7+KVK+rxbzz8hE0yAJ06WpOrgJmmkZd0jxaLlImTsNHB2CxmwkWimoEEwwq/DirLhNxS4SHs34LMxeoRVOxDG39VrQcDe0q+18aCX2SPHRmBcGvcV4x+a6JqwhenMVZiKypQq/RQpeD7PeVSQAh1Vd3zvRB8w1zvoUAHmL9JWCfrnwe2fVDBr/DfE9IpPmYNCbvLhpxAMMYMMS0RzwPCpriCdleJi7wBqKJ/jseQOndNWb028A8jnWzXPMkgbF+P5sj+Tu48XY56E7Oe1NmynMg0EswO3PwdFd9Cevdkbn6CbuSGloK2JQ3P28rnRjzh8LEdYSR+iL3mMpuR7N9BgF")

    items=list()
    inputObj={ "RequesterCredentials": {
                               "eBayAuthToken": "AgAAAA**AQAAAA**aAAAAA**zY2pXg**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6MElIuoC5CEpAydj6x9nY+seQ**/0kGAA**AAMAAA**7/kuig0GXA6zyrQ/D6lHcXQVtH2z/rLeU4EzvA4jqRnDtBEXlUMdK5ZuE0EpkrfiI7bUcY6xVnn9C/6Iajfk9uhKoayDerpacV7wwRbELehUna4jXa57klixCENuF6UbPprzmnbIVt0pdoWNw5Yfa9dSEZb6FKw4eVwWwwABNUOIxd7ozBMVoZwywBQ5JwOKl2U8wzfnxzNH/tiSn5NSkiqOJztVlOT5XZWPB1wlaoZsLrGBxZDEeAQ3C+fKOm5NJIpEn6YCZF7u0SPulv2I4gcXCJVUQ8en7bClXajs4c/Qfo+gelpYHKKeTWVInQbqcEF+OoUcA0deqjYgIxsJ6J0iRXQoaESYV1tZ1zLVvNcxrysuwVpV7Iwjs5alfKQmAgVlBFjstbi3Pgr/NFR3s3srGR6DLoBNfF6w2yP6LE7+KVK+rxbzz8hE0yAJ06WpOrgJmmkZd0jxaLlImTsNHB2CxmwkWimoEEwwq/DirLhNxS4SHs34LMxeoRVOxDG39VrQcDe0q+18aCX2SPHRmBcGvcV4x+a6JqwhenMVZiKypQq/RQpeD7PeVSQAh1Vd3zvRB8w1zvoUAHmL9JWCfrnwe2fVDBr/DfE9IpPmYNCbvLhpxAMMYMMS0RzwPCpriCdleJi7wBqKJ/jseQOndNWb028A8jnWzXPMkgbF+P5sj+Tu48XY56E7Oe1NmynMg0EswO3PwdFd9Cevdkbn6CbuSGloK2JQ3P28rnRjzh8LEdYSR+iL3mMpuR7N9BgF"
                           },
                           "ErrorLanguage": "en_US",
                           "WarningLevel": "High",
                           "GranularityLevel": "Coarse",
                           "StartTimeFrom": "2020-01-30 23:29:25.354049",
                           "StartTimeTo": "2020-04-29 23:29:25.354038",
                           "IncludeWatchCount": "true",
                           "UserID": "aroundmountain",
                           "OutputSelector": [
                               "Title",
                               "ViewItemURL",
                               "SellingStatus",
                               "ListingDuration",
                               "StartTime",
                               "EndTime",
                               "WatchCount",
                               "ItemsPerPage",
                               "PrimaryCategory",
                               "HasMoreItems",
                               "PageNumber",
                               "ReturnedItemCountActual",
                                "PaginationResult"
                           ],
                           "Pagination": {
                               "EntriesPerPage": "100",
                               "PageNumber":"1"

                           }
                       }

    startDateTo =datetime.datetime.now()
    startDateFrom =startDateTo-datetime.timedelta(90)

    for i in range(5):
        inputObj["StartTimeTo"] = startDateTo
        inputObj["StartTimeFrom"] = startDateFrom
        inputObj["Pagination"]["PageNumber"]=1

        while True:
            print(inputObj)
            print('\n')
            response = api.execute('GetSellerList',inputObj).dict()
            if(i==2):
                print("response is ", response)
            if response["ItemArray"] is None:
                break
            currentItems=response["ItemArray"]["Item"]
            items.extend(currentItems)
            print("page number is ",response["PageNumber"])
            print("remaining pages",response["PaginationResult"])
            print("has more number ",response["HasMoreItems"])
            if response["HasMoreItems"]!="true":
                break
            inputObj["Pagination"]["PageNumber"] = int(response["PageNumber"]) + 1
        if i==4:
            startDateTo = startDateTo - datetime.timedelta(6)
            startDateFrom = startDateFrom - datetime.timedelta(6)
        else:
            startDateTo=startDateTo-datetime.timedelta(90)
            startDateFrom=startDateFrom-datetime.timedelta(90)
        print("iteration number ",i)

    print(items,file=open("1.txt","w"))
    updateToGSheet(items)

#print(json.dumps(response,indent=1),file=open("1.txt","w"))
#print(int(time.time())-int(startTime))

#print(response.reply)
#print(response.dict())
#print(response)
#aroundmountain

if __name__=="__main__":
    main()




