import xmltodict
import requests
import json
import datetime
import re

global headers
headers = {"Content-Type":"application/xml",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0", 
"Connection": "close"}

global regex
regex = ".*?([0-9]+)[\n]*" #only the number at the end



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
        
        regexNumber = ".*?([0-9]+)[\n]*" #only the number at the end
        regexPrefix = "(.*?)[0-9]+[\n]*"
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

def clean_newline(address):
    cleanedAddress = address.replace("\n", " ")
    return cleanedAddress

def process_string(address):
    cleanedAddress = clean_newline(address)
    cleanedAddress = remove_useless_whitespace(cleanedAddress)
    return cleanedAddress

def remove_useless_whitespace(address):
    cleanedAddress = address.strip().lower()
    return cleanedAddress

def vehicle_supported_type(s):
    if s == "Tesla only":
        return "Tesla"
    elif s == "BYD only":
        return "BYD"
    else:
        return "General"

def create_range_list(start, end):
    range_list = []
    for i in range(start, end + 1):
        range_list.append(i)
    return range_list

def parking_slot_list(s):
    regexNumber = ".*?([0-9]+)[\n]*" #only the number at the end
    regexPrefix = "(.*?)[0-9]+[\n]*"
    if s == "Tesla only" or s == "BYD only" or s == None or "permit" in s or s == "":
        r = ["No information provided"]
        return r 

    else:
        parking_slot_list = []
        
        data_comma_split = s.split(",")
        
        for element in data_comma_split:
            element = process_string(element)

            isRange = False
            
            if "-" in element:
                isRange = True
                
            if not isRange:
                parking_slot_list.append(element)
            
            if isRange:
                
                data_dash_split = element.split("-")

                item0 = process_string(data_dash_split[0])
                item1 = process_string(data_dash_split[1])

                item0_number = re.findall(regexNumber, item0)[-1]
                item0_prefix = item0[0:item0.find(item0_number)]

                item1_number = re.findall(regexNumber, item1)[-1]
                item1_prefix = item1[:item1.find(item1_number)]

                # print(item0_prefix, item0_number)
                # print(item1_prefix, item1_number)

                rangeList = create_range_list(int(item0_number), int(item1_number))
                # print(rangeList)

                for parkingNumber in rangeList:
                    parking_slot_list.append(item0_prefix + str(parkingNumber))

        return parking_slot_list

def check_public_permit(s):
    if s == None:
        return True
    elif "permit" in s:
        return False
    else:
        return True

def main():
    startTime = datetime.datetime.now()

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
                    "en": process_string(remove_useless_whitespace(station["address"]))
                },
                "streetName": process_string(station["address"]),
                "region": process_string(station["districtL"]),
                "district": process_string(station["districtS"]),
                "locationName": {
                    "zh" : "",
                    "en": process_string(station["location"])
                },
                "geocode":{
                    "WGS84": {
                        "lat": station["lat"],
                        "lng": station["lng"],
                    }
                }
            },
            "provider": process_string(station["provider"]),
            "type": {
                "charging": process_string(station["type"]).split(";"), #standard / semiquick / quick
                "vehicle": vehicle_supported_type(station["parkingNo"]), 
            },
            "publicPermit": check_public_permit(station["parkingNo"]),
            "parkingSlot": parking_slot_list(station["parkingNo"]),
            "updateCheckSum": ""
        }


        newStationsList.append(newStationData)
        counter += 1

        if counter % 20 == 0:
            x = open("cleaned_EV_raw.json","w")
            x.write(json.dumps(newStationsList, indent=4))
            x.close()



    timeNow =  datetime.datetime.now()
    print(
        "Total use {} seconds to run".format(round((timeNow - startTime).total_seconds()))
    )


if __name__ == "__main__":
    main()