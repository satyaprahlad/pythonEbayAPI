import traceback

from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping

import datetime
import time
import gspread.client
from oauth2client.service_account import ServiceAccountCredentials

sellerIdFromSheet=""
noOfMonths=""

def updateToGSheet(data ,error=None,sellerIdFromSheet="",noOfMonths="0"):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)
    client = gspread.authorize(creds)

    outputSheet = client.open("OrderInformationsWork").worksheet("Output")
    allRowsValues = [
                     ['','','','Seller Details : '+str(sellerIdFromSheet)+' For '+str(noOfMonths)+' Month(s)','','','Sheet Last Updated at: '+str(datetime.datetime.now())],
                     [],
                     ['Title', 'Price', 'Watch','Sold', 'CategoryID','Duration', 'Hit Count' ]]

    if (error is not None):
        errors = ['Failed to update sheet with reason : ', str(error), ' at ', str(datetime.datetime.now())]
        print("error with ", error)
        outputSheet.clear()
        outputSheet.append_row(errors)
        raise Exception(error)
        return

    #allRowsValues.append(eachRow1)
    for eachItem in data:
        #print(eachItem)
        watchCont=0 if eachItem['listingInfo'].get('watchCount') is None else int(eachItem['listingInfo']['watchCount'])
        QuantitySold=0 if eachItem.get('QuantitySold') is None else int(eachItem['QuantitySold'])
        HitCount=0 if eachItem.get('HitCount') is None else int(eachItem['HitCount'])
        eachRow = [eachItem.get('title'), float(eachItem['sellingStatus']['currentPrice']['value']),
                   watchCont,
                   QuantitySold,
                   int(eachItem['primaryCategory']['categoryId']),
                   int(eachItem['DurationCalc']),HitCount]
        allRowsValues.append(eachRow)

    outputSheet.clear()
    outputSheet.append_rows(allRowsValues)

    #For starting heading
    outputSheet.format("A1:F1", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 1.0,
        "green": 0.0,
        "blue": 0.0
    }}})

    #for each attribute
    outputSheet.format("A3:I3", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 1.0,
        "green": 0.0,
        "blue": 0.0
    }}})
    #to print timestamp at right side of sheet
    outputSheet.format("G1:I1", {"textFormat": {"bold": False, "fontSize": 12, "foregroundColor": {
        "red": 0.0,
        "green": 1.0,
        "blue": 0.0
    }}})#ok
    # reset format

    outputSheet.merge_cells('D1:F1')
    outputSheet.merge_cells('G1:I1')

    client.open("OrderInformationsWork").worksheet("Input").update_cell(4,2,"")
    # clearing input value so that script will not process repeatedly.



def getFromSheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)

    client = gspread.authorize(creds)

    input = client.open("OrderInformationsWork").worksheet("Input")
    sellerIdFromSheet = input.cell(4,3).value.strip()
    noOfMonths = int(input.cell(5,2).value)
    return (sellerIdFromSheet,noOfMonths)





def updateQuantitySoldEtc(items):
    #this multiple items api takes at a time 20 itemids only. So calling it repeatedly.
    api = Shopping(config_file=None, domain='open.api.ebay.com', appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe",
                      devid="6c042b69-e90f-4897-9045-060858248665",
                      certid="PRD-bce464fbd03b-273a-4416-a299-7d41"
                      )


    inputObj={"ItemID": [],"IncludeSelector": "Details"
}
    j=0
    _=0
    tic=time.perf_counter()
    while _ < (len(items)):
        #print("_ values is: ",_," , ",j)
        if _+20 > len(items):
            j=len(items)
        else:
            j=_+20
        inputObj["ItemID"]=list(map(lambda x:x['itemId'],items[_:j]))

        #print("before adding sold, hitcount ",items[_:j])
        response = api.execute('GetMultipleItems', inputObj).dict()
        #print("response after executing multiple api call: ",response)
        for i in range(len(response['Item'])):
            items[_+i]['QuantitySold']=response['Item'][i].get('QuantitySold')
            items[_+i]['HitCount']=response['Item'][i].get('HitCount')
        _=j
        #print("remaining items to process ",len(items)-i)

    #correcting duration to start and end dates diff
    for item in items:
        #print("start time and ",item['listingInfo']['startTime']," end time; ", item['listingInfo']['endTime'])
        startTime=datetime.datetime.strptime(item['listingInfo']['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        endTime=datetime.datetime.strptime(item['listingInfo']['endTime'],"%Y-%m-%dT%H:%M:%S.%fZ")
        item['DurationCalc']=(endTime.__sub__(startTime)).days
        #print("duration is , ",item['DurationCalc'])
    toc = time.perf_counter()
    print(f"stopwatch: {toc - tic}")

def main():
    tic=time.perf_counter()
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
            "StartTimeFrom": "",
            "StartTimeTo": "",
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
            if(noOfMonths==1):#one month only
                queryRepeats=queryRepeats+1
                startDateFrom = startDateTo - datetime.timedelta(30)
            elif(queryRepeats==4): #need to include (4*90) obvious and 6 days for a year
                queryRepeats=5

            for i in range(queryRepeats):
                inputObj["StartTimeTo"] = startDateTo
                inputObj["StartTimeFrom"] = startDateFrom
                inputObj["paginationInput"]["pageNumber"] = 1
                print("iteration number ", i)
                print(inputObj["StartTimeTo"], "  ", inputObj["StartTimeFrom"])
                if True:

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

            #print(items, file=open("1.txt", "w"))
            print("total items: ",len(items))
            print("now adding details like hit count and quantity sold")
            updateQuantitySoldEtc(items)
            updateToGSheet(items,None,sellerIdFromSheet,noOfMonths)
    except Exception as error:
        traceback.print_stack()
        updateToGSheet(None, error=error)

    toc=time.perf_counter()

    print(f"time taken {toc-tic}")
# print(json.dumps(response,indent=1),file=open("1.txt","w"))
# print(int(time.time())-int(startTime))

# print(response.reply)
# print(response.dict())
# print(response)
# aroundmountain

if __name__ == "__main__":
    main()
