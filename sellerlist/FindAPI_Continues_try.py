import copy
import concurrent.futures
import getpass
import sys
from sys import exc_info

from ebaysdk.finding import Connection as Finding
from ebaysdk.shopping import Connection as Shopping
import logging

import threading
import datetime
import time
import gspread.client
from oauth2client.service_account import ServiceAccountCredentials

thread_local=threading.local()

#logging.basicConfig(filename="FindAPI.log",

 #                   filemode='w')
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)

def updateToGSheet(data ,error=None,sellerIdFromSheet="",noOfMonths="0"):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)
    client = gspread.authorize(creds)

    outputSheet = client.open("OrderInformationsWork").worksheet("Output")
    allRowsValues = [
                     ['','','','Seller Details : '+str(sellerIdFromSheet)+' For '+str(noOfMonths)+' Month(s)','','','Sheet Last Updated at: '+str(datetime.datetime.now())+' by '+getpass.getuser()],
                     [],
                     ['Title', 'Price', 'Watch','Sold', 'CategoryID','Duration', 'Viewed','TimeLeft before Listing Ends' ]]

    if (error is not None):
        errors = ['Failed to update sheet with reason : ', str(error), ' at ', str(datetime.datetime.now())]
        logger.exception(f"error with {error}")
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
                   int(eachItem.get('DurationCalc'))
            ,HitCount, eachItem['sellingStatus']['timeLeft']]
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
    outputSheet.format("I1:M1", {"textFormat": {"bold": False, "fontSize": 12, "foregroundColor": {
        "red": 0.0,
        "green": 1.0,
        "blue": 0.0
    }}})#ok
    # reset format

    outputSheet.merge_cells('D1:F1')
    outputSheet.merge_cells('G1:I1')

    inputSheet=client.open("OrderInformationsWork").worksheet("Input")

    inputSheet.format("B4:B4", {"backgroundColor": {
    "red": 1.0,
    "green": 0.8,
    "blue": 0.3
    },"textFormat": {"bold": False, "fontSize": 12}})
    inputSheet.update_cell(4,2,"")
    # clearing input value so that script will not process repeatedly.

def get_session():
    if not hasattr(thread_local, "api"):
        thread_local.api = Shopping(config_file=None, domain='open.api.ebay.com',
                                    appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe",
                                    devid="6c042b69-e90f-4897-9045-060858248665",
                                    certid="PRD-bce464fbd03b-273a-4416-a299-7d41"
                                    )
    return thread_local.api


def getFromSheet():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)

    client = gspread.authorize(creds)

    input = client.open("OrderInformationsWork").worksheet("Input")
    sellerIdFromSheet = input.cell(4,3).value.strip()
    noOfMonths = int(input.cell(5,2).value)
    return (sellerIdFromSheet,noOfMonths)


thread_local_FindingApi_Session=threading.local()
def getFindingApiSession():
    if not hasattr(thread_local_FindingApi_Session,"api"):
        thread_local_FindingApi_Session.api=Finding(config_file=None, domain='svcs.ebay.com', appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe",
                  devid="6c042b69-e90f-4897-9045-060858248665",
                  certid="PRD-bce464fbd03b-273a-4416-a299-7d41"
                  )
    return thread_local_FindingApi_Session.api

def retrieveFromSecondPage(inputObj):
    api=getFindingApiSession()
    response = api.execute('findItemsAdvanced', inputObj).dict()
    #logger.info(f" thread name {threading.currentThread().name } result is : {response}")
    return response


def main():
    while True:
        try:
            tic=time.perf_counter()
            ebayFunction()
            toc=time.perf_counter()
            logger.info(f"total time taken: {toc-tic}")
            time.sleep(60)
        except:logger.exception("Exception at processing")



def eachMonthRunner(eachMonthInfo):
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
            "pageNumber": "0"

        }
    }

    startDateTo = eachMonthInfo.get('startDateTo')
    sellerIdFromSheet=eachMonthInfo.get('sellerIdFromSheet')
    startDateFrom = startDateTo - datetime.timedelta(6)


    inputObj["itemFilter"]["value"] = sellerIdFromSheet
        # queryRepeats = int(noOfMonths / 3)
        # if (noOfMonths == 1):  # one month only
        #     queryRepeats = queryRepeats + 1
        #     startDateFrom = startDateTo - datetime.timedelta(30)
        # elif (queryRepeats == 4):  # need to include (4*90) obvious and 6 days for a year
        #     queryRepeats = 5
        tic = time.perf_counter()

        inputObj["StartTimeTo"] = startDateTo
        inputObj["StartTimeFrom"] = startDateFrom
        interval=datetime.timedelta(startDateTo,startDateFrom)
        inputObj["paginationInput"]["pageNumber"] = 1
        #logger.info(f"iteration number ")
        logger.info(f"sad{inputObj['StartTimeTo']} and {inputObj['StartTimeFrom']}")

        items=list()a

        while(interval>0):
            inputObj["StartTimeFrom"] = startDateFrom
            response = getFindingApiSession().execute('findItemsAdvanced', inputObj).dict()
            if response.get("searchResult") is None:
                logger.info(f"no result at month: {startDateTo}")
                return items
            currentItems = response["searchResult"]["item"]
                        # print("lenght of items , ", len(items))
            # print("page number is ", response["PageNumber"])
            # print("remaining pages", response["PaginationResult"])
            # print("has more number ", response["HasMoreItems"])
            remainingPages = int(response["paginationOutput"]["totalPages"]) - int(
                response["paginationOutput"]["pageNumber"])
            if remainingPages <= 99:
                break
            if remainingPages > 99:interval=int(interval/2)

        interval= interval if interval>0 else 1

        logger.info(f"remaining pages: {remainingPages}")
            # query allows only upto max 100 pages
        remainingPages = min(99, remainingPages)
        multiThreadInputObjects = [copy.deepcopy(inputObj) for _ in range(remainingPages)]
            for i in range(remainingPages):
                multiThreadInputObjects[i]["paginationInput"]["pageNumber"] = i + 2
            # logger.debug(multiThreadInputObjects)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(5, remainingPages / 20)) as executor:
                searchResults = []
                searchResults = executor.map(retrieveFromSecondPage, multiThreadInputObjects)
                logger.info("underr multithread")
                for searchResult in searchResults:
                    items.extend(searchResult["searchResult"]["item"])
                executor.shutdown()

            # if i == 3:
            #     startDateFrom = startDateFrom - datetime.timedelta(6)  # just for last 6 days in 365/366  days
            # else:
            startDateFrom = startDateFrom - datetime.timedelta(6)
            startDateTo = startDateTo - datetime.timedelta(6)


def ebayFunction():
    api = Finding(config_file=None, domain='svcs.ebay.com', appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe",
                  devid="6c042b69-e90f-4897-9045-060858248665",
                  certid="PRD-bce464fbd03b-273a-4416-a299-7d41"
                  )
    sellerIdFromSheet, noOfMonths = getFromSheet();
    logger.info(f"seller id fro sheet  {sellerIdFromSheet}")
    logger.info(f"no of months {str(noOfMonths)}")
    items=list()
    eachMonthInputs=list()
    for _ in noOfMonths:
        eachMonthInput=dict()
        eachMonthInput.__setitem__("startDateTo",datetime.datetime.now()-datetime.timedelta(_*30))
        eachMonthInput.__setitem__("sellerIdFromSheet",sellerIdFromSheet)
    eachMonthInputs.append(eachMonthInput)
    tic=time.perf_counter()
    with concurrent.futures.ProcessPoolExecutor(max_workers=noOfMonths) as executor:
        results=executor.map(eachMonthRunner,eachMonthInputs)
        for result in results:
            items.extend(result)

    # print(items, file=open("1.txt", "w"))
        # setting duration count
    for item in items:
            # print("start time and ",item['listingInfo']['startTime']," end time; ", item['listingInfo']['endTime'])
        startTime = datetime.datetime.strptime(item['listingInfo']['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        endTime = datetime.datetime.strptime(item['listingInfo']['endTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            #item['DurationCalc']= (endTime.__sub__(startTime)).days
        item['DurationCalc'] = (endTime.__sub__(startTime)).days
    toc=time.perf_counter()
    logger.info(f"search took {toc-tic} time with items: {len(items)}")
    logger.info("now adding details like hit count and quantity sold")
    items=getGood(items)

    updateToGSheet(items, None, sellerIdFromSheet, noOfMonths)
    logger.info("completed")

def getGood(items):
    logger.info("shopping")
    itemIdSet = set(map(lambda x: x['itemId'], items))
    noDuplicates = list()
    print("set size is ",len(itemIdSet))
    for x in items:
        if x['itemId'] in itemIdSet:
            itemIdSet.remove(x['itemId'])
            noDuplicates.append(x)

    logger.info(f"no of duplicates: {len(items)-len(noDuplicates)}")
    items = noDuplicates
    inputObj = {"ItemID": [], "IncludeSelector": "Details"}
    inputObjects = []
    j = 0
    _ = 0
    for item in items:
        # print("start time and ",item['listingInfo']['startTime']," end time; ", item['listingInfo']['endTime'])
        startTime = datetime.datetime.strptime(item['listingInfo']['startTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        endTime = datetime.datetime.strptime(item['listingInfo']['endTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        item['DurationCalc'] = (endTime.__sub__(startTime)).days
        item['QuantitySold']=0
        item['HitCount']=0
        logger.info(item['itemId'])
    tic = time.perf_counter()
    while _ < (len(items)):
        logger.info(f"{_} out of {len(items)}")
        if _ + 20 > len(items):
            j = len(items)
        else:
            j = _ + 20
        inputObj["ItemID"] = list(map(lambda x: x['itemId'], items[_:j]))

        # print("before adding sold, hitcount ",items[_:j])
        try:
            response = get_session().execute('GetMultipleItems', inputObj).dict()
        # print("response after executing multiple api call: ",response)

        except ConnectionError as err:
            logger.info("got exception while getmultipleitems",exc_info=True)
            print("exception at connection",err)
            print(err.response().dict())
            break
        except:
            print("exception at connection")
            logger.exception("got exeption not ConnectionError")
            break
        else:
            if type(response.get('Item'))==list:
                for i in range(len(response['Item'])):
                    items[_ + i]['QuantitySold'] = response['Item'][i].get('QuantitySold')
                    items[_ + i]['HitCount'] = response['Item'][i].get('HitCount')
            elif type(response.get('Item')) == dict:
                    print(items[_:j])
                    print(response['Item'])
                    items[_]['QuantitySold'] = response['Item'].get('QuantitySold')
                    items[_]['HitCount'] = response['Item'].get('HitCount')
            else:
                print("Din't get any response due to time out.")
                print(response.get('Errors'))
                break

        _ = j

        # print("remaining items to process ",len(items)-i)
    # correcting duration to start and end dates diff
        # print("duration is , ",item['DurationCalc'])
    toc = time.perf_counter()
    logger.info(f"stopwatch: {toc-tic}")
    #logger.info(f"lengthof input {len(inputObjects)}")
    return items


if __name__ == "__main__":
    main()
