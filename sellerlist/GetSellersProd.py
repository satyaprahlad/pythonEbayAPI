import logging
import sys
import threading
import traceback
import getpass

from ebaysdk.trading import Connection as Trading
from ebaysdk.shopping import Connection as Shopping
import datetime
import time
import gspread.client
from oauth2client.service_account import ServiceAccountCredentials
thread_local=threading.local()
logging.basicConfig(filename="GetSellar.log",
                    filemode='w')# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)


def updateToGSheet( data,error=None):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("ebayPractice-f9627f3e653b.json", scope)
    client = gspread.authorize(creds)
    sheet1 = client.open("OrderInformationsWork").worksheet("aroundmountain")
    eachRow1 = ['Title', 'Price', 'Watch',
               'Sold', 'CategoryID',
               'Duration','Viewed','','Last Updated at: '+str(datetime.datetime.now())+' by '+getpass.getuser()]
    #heading
    if (error is not None):
        errors=['Failed to update sheet with reason : '+str(error)+' at '+str(datetime.datetime.now())]
        print("error with ",error)
        print()
        logger.debug(error)
        sheet1.clear()
        sheet1.append_row(errors)
        return
    allRowsValues = list()
    allRowsValues.append(eachRow1)
    for eachItem in data:
        #print(eachItem)
        eachRow = [eachItem['Title'], float(eachItem['SellingStatus']['CurrentPrice']['value']), int(eachItem['WatchCount']),
                   int(eachItem['SellingStatus']['QuantitySold']), int(eachItem['PrimaryCategory']['CategoryID']), eachItem['ListingDuration'],eachItem['HitCount']]
        allRowsValues.append(eachRow)

    #print("all rows are ",allRowsValues)
    sheet1.clear()
    sheet1.append_rows(allRowsValues)

    sheet1.format("A1:G1", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 1.0,
        "green": 0.0,
        "blue": 0.0
    }}})

    sheet1.format("H1:I1", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 0.0,
        "green": 1.0,
        "blue": 0.0
    }}})
    #reset format
    sheet1.format("H2:I2", {"textFormat": {"bold": True, "fontSize": 12, "foregroundColor": {
        "red": 0.0,
        "green": 0.0,
        "blue": 0.0
    }}})


def get_session():
    if not hasattr(thread_local, "api"):
        thread_local.api = Shopping(config_file=None, domain='open.api.ebay.com',
                                    appid="SatyaPra-MyEBPrac-PRD-abce464fb-dd2ae5fe",
                                    devid="6c042b69-e90f-4897-9045-060858248665",
                                    certid="PRD-bce464fbd03b-273a-4416-a299-7d41"
                                    )
    return thread_local.api

def getGood(items):
    logger.debug("shopping")

    inputObj = {"ItemID": [], "IncludeSelector": "Details"}
    inputObjects = []
    j = 0
    _ = 0
    for item in items:
        item=eval(str(item))
        print(f"item type{type(item)} and {item.get('HitCount')}")
        # print("start time and ",item['listingInfo']['startTime']," end time; ", item['listingInfo']['endTime'])
        startTime = datetime.datetime.strptime(item['ListingDetails']['StartTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        endTime = datetime.datetime.strptime(item['ListingDetails']['EndTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        item['DurationCalc'] = (endTime.__sub__(startTime)).days
        if item.get('HitCount') is None:
            item['HitCount']=0
    tic = time.perf_counter()
    while _ < (len(items)):
        # print("_ values is: ",_," , ",j)
        if _ + 20 > len(items):
            j = len(items)
        else:
            j = _ + 20
        inputObj["ItemID"] = list(map(lambda x: x['ItemID'], items[_:j]))
        try:
            response = get_session().execute('GetMultipleItems', inputObj).dict()
        except ConnectionError as err:
            logger.debug("got exception while getmultipleitems",exc_info=True)
            traceback.print_exc()
            print("exception at connection")
            traceback.print_exc()
            break
        except:
            print("exception at connection")
            traceback.print_exc()
            logger.exception("got exeption not ConnectionError")
            break
        else:
            print(response)
            if type(response.get('Item'))==list:
                for i in range(len(response['Item'])):
                    items[_ + i]['HitCount'] = response['Item'][i].get('HitCount')
            elif type(response.get('Item'))==dict:
                    items[_]['HitCount'] = response['Item'].get('HitCount')
            else:
                print("Din't get any response due to time out.")
                print(response.get('Errors'))
                break
        _ = j

    toc = time.perf_counter()
    logger.debug(f"stopwatch: {toc-tic}")
    logger.debug(f"lengthof input {len(inputObjects)}")



def main():
    try:

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
                               "PaginationResult",
                               "itemId",
                               "HitCount",
                               "HitCounter"
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
            print("iteration number ", i)
            #print(inputObj["StartTimeTo"], "  ", inputObj["StartTimeFrom"])
            while True:
            #print(inputObj)

                print('\n')
                response = api.execute('GetSellerList',inputObj).dict()
                #file=open("1.txt","w")
                #print(response)
                if response["ItemArray"] is None:
                    print("no result at i ",i)
                    break
                currentItems=response["ItemArray"]["Item"]
                items.extend(currentItems)
                print("page number is ",response["PageNumber"])
                print("remaining pages",response["PaginationResult"])
                print("has more number ",response["HasMoreItems"])
                if response["HasMoreItems"]!="true":
                    break
                inputObj["Pagination"]["PageNumber"] = int(response["PageNumber"]) + 1
            if i==3:
                startDateFrom = startDateFrom - datetime.timedelta(6) #just for last 6 days in 365/366  days
            else:
                startDateFrom=startDateFrom-datetime.timedelta(90)
            startDateTo = startDateTo - datetime.timedelta(90)

        #print(items,file=open("1.txt","w"))
        print("setting hitcount etc")
        getGood(items)
        updateToGSheet(items)
    except Exception as error:
        traceback.print_exc()
        print(sys.exc_info())
        updateToGSheet(None,error=error)
#print(json.dumps(response,indent=1),file=open("1.txt","w"))
#print(int(time.time())-int(startTime))

#print(response.reply)
#print(response.dict())
#print(response)
#aroundmountain

if __name__=="__main__":
    main()




