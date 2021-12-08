import xmltodict
import requests
import json
import datetime
import re

headers = {"Content-Type":"application/xml",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0", 
"Connection": "close"}

def download_files():
    #download the file into memory
    res = requests.get("https://opendata.clp.com.hk/GetChargingSectionXML.aspx?lang=EN", headers=headers)

    #write xml file into the HDD
    myfile = open("EV_raw.xml", "w")
    myfile.write(res.text)

    return res

def convert_XMLtoJSON(res):
    xmltodict_data = xmltodict.parse(res.content)
    print(type(xmltodict_data))

    json_data= json.dumps(xmltodict_data, indent=4, sort_keys=True)
    #print(json_data)
    x= open("EV_raw.json","w")
    x.write(json_data)
    x.close()

def remove_useless():
    x= open("EV_raw.json")
    data = json.load(x)

    # y = open("EV_data_c1.json")
    station_List = []

    for station in data["ChargingStationData"]["stationList"]["station"]:
        if "img" in station:
            del station["img"]
        if "no" in station:
            del station["no"]
        station_List.append(station)
    return station_List

def process_parkingNo(station):
    # for station in station_List:
    parkingNo = station["parkingNo"]
    parking_Count = 0

    if parkingNo == None:
        parking_Count = "Unknown"

    elif parkingNo == "Tesla only":
        parking_Count = "Unknown (Tesla only)"

    elif "," in parkingNo:
        parkingNo_comma_split = parkingNo.split(",")
        #parkingNo_List = parkingNo_comma_split
        
        for element in parkingNo_comma_split:
            element = element.strip()
            
            if "-" in element:
                parkingNo_dash_split = element.split("-")

                item0 = parkingNo_dash_split[0].strip()
                item1 = parkingNo_dash_split[1].strip()
                # for item in parkingNo_dash_split:
                # item = item.strip()
                
                regex = ".*?([0-9]+)[\n]*"
                item0_number_only = re.findall(regex, item0)[-1]
                item1_number_only = re.findall(regex, item1)[-1]
                count = int(item1_number_only) - int(item0_number_only) + 1
                parking_Count = parking_Count + count

            else:
                parking_Count += 1

                    # if item.isnumeric():
                    #     #123
                    #     count = int(item[1]) - int(item[0]) + 1
                    # else:
                    #     #ABC, #$2234, #112, #A123
                    # '^[0-9]+$'
        
    
    elif "-" in parkingNo:
        parkingNo_dash_split = parkingNo.split("-")

        item0 = parkingNo_dash_split[0].strip()
        item1 = parkingNo_dash_split[1].strip()
        # for item in parkingNo_dash_split:
        # item = item.strip()
        
        regex = ".*?([0-9]+)[\n]*"
        item0_number_only = re.findall(regex, item0)[-1]
        item1_number_only = re.findall(regex, item1)[-1]
        count = int(item1_number_only) - int(item0_number_only) + 1
        parking_Count = parking_Count + count
    
    
    else:
        parking_Count = 1
        
        #if is null
        #if have - (no ,) than calculate
        #if no - or , than should have only one parking_Count

    
    return parking_Count

'''
ParkingNo Types:
number-number
number - number
number, number
letternumber
'''



def main():
    startTime = datetime.datetime.now()
    
    # convert_XMLtoJSON(download_files())
    # print(remove_useless())
    cleanedData = remove_useless()

    x= open("EV_raw.json")
    data = json.load(x)

    newStationsList =[]
    counter = 0

    for station in data["ChargingStationData"]["stationList"]["station"]:

        """
        "vehicle" value should be Tesla, BYD or General
        """
        newStationData = {
            "uuid": station["no"],
            "address": {
                "full": {
                    "zh": "",
                    "en": "Wan Chai Tower and Immigration Tower"
                },
                "streetName": station["address"],
                "region": "Kowloon",
                "district":  "Yau Tsim Mong",
                "locationName": {
                    "zh" : "灣仔政府大樓及入境事務大樓",
                    "en": "Pioneer Centre Car Park"
                },
                "geocode":{
                    "WGS84": {
                        "lat": station["lat"],
                        "lng": station["lng"],
                    }
                }
            },
            "provider": "Others",
            "type": {
                "charging": ["Standard", "SemiQuick"],
                "vehicle": "Tesla", 
            },
            "publicPermit": "true",
            "parkingSlot": process_parkingNo(station),
            "updateCheckSum": "wegwegewg"
        }


        newStationsList.append(newStationData)
        counter += 1

        if counter % 20 == 0:
            x = open("cleaned_EV_raw.json","w")
            x.write(newStationsList)
            x.close()



    timeNow =  datetime.datetime.now()
    print(
        "Total use {} seconds to run".format(round((timeNow - startTime).total_seconds()))
    )


if __name__ == "__main__":
    main()