import traceback

from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping

import datetime
import time
import gspread.client
from oauth2client.service_account import ServiceAccountCredentials


def updateToGSheet(data,sellerIdFromSheet,noOfMonths ,error=None):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)

    client = gspread.authorize(creds)

    sheet1 = client.open("OrderInformationsWork").worksheet("Output")
    allRowsValues = [
                     ['','','','Seller Details : '+sellerIdFromSheet+' For '+noOfMonths+' Months','','','Sheet Last Updated at: '+str(datetime.datetime.now())],
                     [],
                     ['Title', 'Price', 'Watch',
                'Sold', 'CategoryID',
                'Duration', 'Hit Count' ]]

    # heading
    if (error is not None):
        errors = ['Failed to update sheet with reason : ', str(error), ' at ', str(datetime.datetime.now())]
        print("error with ", error)
        raise Exception(error)
        sheet1.clear()
        sheet1.append_row(errors)
        return

    #allRowsValues.append(eachRow1)
    for i in range(len(data)):
        eachItem = data[i]
        print(eachItem)
        watchCont=0 if eachItem['listingInfo'].get('watchCount') is None else int(eachItem['listingInfo']['watchCount'])
        QuantitySold=0 if eachItem.get('QuantitySold') is None else int(eachItem['QuantitySold'])
        HitCount=0 if eachItem.get('HitCount') is None else int(eachItem['HitCount'])
        eachRow = [eachItem['title'], float(eachItem['sellingStatus']['currentPrice']['value']),
                   watchCont,
                   QuantitySold,
                   int(eachItem['primaryCategory']['categoryId']),
                   int(eachItem['DurationCalc']),HitCount]

        allRowsValues.append(eachRow)

    sheet1.clear()
    sheet1.append_rows(allRowsValues)

    sheet1.format("A1:F1", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 1.0,
        "green": 0.0,
        "blue": 0.0
    }}})
    sheet1.format("A3:I3", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 1.0,
        "green": 0.0,
        "blue": 0.0
    }}})

    sheet1.format("G1:I1", {"textFormat": {"bold": False, "fontSize": 12, "foregroundColor": {
        "red": 0.0,
        "green": 1.0,
        "blue": 0.0
    }}})#ok
    # reset format

    sheet1.merge_cells('D1:F1')
    sheet1.merge_cells('G1:I1')

    inputSheet = client.open("OrderInformationsWork").worksheet("Input")
    inputSheet.update_cell(4,2,"")# clearing input value so that script will process repeatedly.



def getFromSheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)

    client = gspread.authorize(creds)

    input = client.open("OrderInformationsWork").worksheet("Input")
    return (input.cell(4,2).value.strip(),int(input.cell(5,2).value))



def updateQuantitySoldEtc(items):
    #this multiple items api takes at a time 20 itemids only. So calling it repeatedly.
    api=api = Shopping(config_file=None, domain='open.api.ebay.com', appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe",
                      devid="6c042b69-e90f-4897-9045-060858248665",
                      certid="PRD-bce464fbd03b-273a-4416-a299-7d41"
                      )


    inputObj={
   "ItemID": [],
   "IncludeSelector": "Details"
}
    j=0
    _=0
    while _ < (len(items)):
        print("_ values is: ",_," , ",j)
        if _+20 > len(items):
            j=len(items)
        else:
            j=_+20
        inputObj["ItemID"]=list(map(lambda x:x['itemId'],items[_:j]))

        #print("before adding sold, hitcount ",items[_:j])
        response = api.execute('GetMultipleItems', inputObj).dict()
        #print("response after executing multiple api call: ",response)
        for i in range(len(response['Item'])):
            items[_+i]['QuantitySold']=response['Item'][i]['QuantitySold']
            items[_+i]['HitCount']=response['Item'][i]['HitCount']
        _=j
        print("remaining items to process ",len(items)-i)

    #correcting duration to start and end dates diff
    for item in items:
        #print("start time and ",item['listingInfo']['startTime']," end time; ", item['listingInfo']['endTime'])
        startTime=datetime.datetime.strptime(item['listingInfo']['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        endTime=datetime.datetime.strptime(item['listingInfo']['endTime'],"%Y-%m-%dT%H:%M:%S.%fZ")
        item['DurationCalc']=(endTime.__sub__(startTime)).days
        #print("duration is , ",item['DurationCalc'])


def main():
    try:

        api = Finding(config_file=None, domain='svcs.ebay.com', appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe",
                      devid="6c042b69-e90f-4897-9045-060858248665",
                      certid="PRD-bce464fbd03b-273a-4416-a299-7d41"
                      )

        items = list()
        inputObj = {
            "itemFilter": {
                "name": "Seller",
                "value": ""
            },
            "OutputSelector": [
                "Title",
                "itemId",
                "ViewItemURL",
                "SellingStatus",
                "ListingDuration",
                "listingInfo"
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
            "StartTimeFrom": "2020-01-30 23:29:25.354049",
            "StartTimeTo": "2020-04-29 23:29:25.354038",
            "IncludeWatchCount": "true",

            "paginationInput": {
                "entriesPerPage": "100",
                "pageNumber": "1"

            }
        }

        startDateTo = datetime.datetime.now()
        startDateFrom = startDateTo - datetime.timedelta(90)
        sellerIdFromSheet,noOfMonths=getFromSheet();
        print("seller id fro sheet ",sellerIdFromSheet)
        print("no of months ",noOfMonths)
        if sellerIdFromSheet is not None and len(sellerIdFromSheet)>0:

            inputObj["itemFilter"]["value"]=sellerIdFromSheet
            queryRepeats=int(noOfMonths/3)
            if(queryRepeats==0):#one month only
                queryRepeats=queryRepeats+1
                startDateFrom = startDateTo - datetime.timedelta(30)
            if(queryRepeats==4):
                queryRepeats=5

            for i in range(queryRepeats):
                inputObj["StartTimeTo"] = startDateTo
                inputObj["StartTimeFrom"] = startDateFrom
                inputObj["paginationInput"]["pageNumber"] = 1
                print("iteration number ", i)
                print(inputObj["StartTimeTo"], "  ", inputObj["StartTimeFrom"])
                while True:

                    response = api.execute('findItemsAdvanced', inputObj).dict()
                    #print(response)
                    if response["searchResult"] is None:
                        print("no result at i ", i)
                        break
                    currentItems = response["searchResult"]["item"]
                    items.extend(currentItems)
                    #print("lenght of items , ", len(items))
                #print("page number is ", response["PageNumber"])
                #print("remaining pages", response["PaginationResult"])
                #print("has more number ", response["HasMoreItems"])
                    remainingPages=int(response["paginationOutput"]["totalPages"])-int(response["paginationOutput"]["pageNumber"])

                    if remainingPages==0:
                        break
                    inputObj["paginationInput"]["pageNumber"] = int(response["paginationOutput"]["pageNumber"]) + 1
                if i == 3:
                    startDateFrom = startDateFrom - datetime.timedelta(6)  # just for last 6 days in 365/366  days
                else:
                    startDateFrom = startDateFrom - datetime.timedelta(90)
                startDateTo = startDateTo - datetime.timedelta(90)

            print(items, file=open("1.txt", "w"))
            print("total items: ",len(items))
            print("now adding details like hit count and quantity sold")
            updateQuantitySoldEtc(items)
            updateToGSheet(items,sellerIdFromSheet,noOfMonths)
    except Exception as error:
        traceback.print_stack()
        updateToGSheet(None, error=error)


# print(json.dumps(response,indent=1),file=open("1.txt","w"))
# print(int(time.time())-int(startTime))

# print(response.reply)
# print(response.dict())
# print(response)
# aroundmountain

if __name__ == "__main__":
    main()
