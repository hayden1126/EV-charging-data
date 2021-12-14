import re
list = ["D0D042 - D0D052, D106 - D112", "3177-3186, 3189-3206", "D73-D75", "22, 41, 64", "25", "D104", ""]

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

for ele in list:
    print(parking_slot_list(ele))
    print()
    print()