__all__=["dictHasKey","blockSize"]
def atoi(text):
    return int(text) if text.lstrip("-").lstrip("+").isdigit() else text

def natural_keys(text):
    import re
    return [ atoi(c) for c in re.split(r'([-+]?\d+)', text) ]

MONTH_DAYS=[31,28,31,30,31,30,31,31,30,31,30,31]
SECS_PER_MINUTE=60
MINUTES_PER_HOUR=60
HOURS_PER_DAY=24
DAYS_PER_MONTH=30
#get how many should be in each partition when
#id = the partition, p= how many total partitions, n=how many total items there are, function is what to cast result as (int|float)
def blockSize(id,p,n,function=int):
    def Block_low(id,p,n):
        import numpy as np
        return np.floor(id*n/float(p))
    def Block_high(id,p,n):
        return Block_low(id+1,p,n) -1

    return function(Block_high(id,p,n)-Block_low(id,p,n) +1)
def countInterval(interval):
    components = interval.split("-")
    if len(components) > 1:
        #ok we have a hyphen
        start = int(components[0])
        end = int(components[1])
        return end-start+1
    else:
        return 1
def subtractFromInterval(amount,interval):
    components = interval.split("-")
    if len(components) > 1:
        #ok we have a hyphen
        start = int(components[0])
        end = int(components[1])
        total = end-start+1
        if total > amount:
            #there is something left
            newStart = start+amount
            #do we require a hyphen?
            if newStart == end:
                if amount > 1:
                    return str(newStart),amount,f"{start}-{start+amount-1}"
                else:
                    return str(newStart),amount,f"{start}"
            else:
                if amount > 1:
                    return f"{newStart}-{end}",amount,f"{start}-{start+amount-1}"
                else:
                    return f"{newStart}-{end}",amount,f"{start}"
        else:
            #there is nothing left, we subtracted the whole thing
            return "",total,f"{start}-{end}"
        
    else:
        #we don't have a hyphen, so there is one resource
        return "",1,interval
def getComponentValues(component):
    components = component.split("-")
    if len(components) > 1:
        #ok we have a hyphen
        ourList = list(range(int(components[0]),int(components[1])+1,1))
        return ourList
    else:
        return [int(components[0])]
def getIntervalValues(interval):
    components = interval.split(" ")
    myList = []
    for component in components:
        myList = myList + getComponentValues(str(component))
    myList.sort()
    return set(myList)

def countTotalInterval(interval):
    components = interval.split(" ")
    total = 0
    for component in components:
        total+=countInterval(component)
    return total
def subtractFromTotalInterval(amount,interval):
    components = interval.split(" ")
    leftOverComponents = []
    subtractedComponents = []
    skip = False
    for component in components:
        
        if skip == False:
         
            leftOverInterval,amountSubtracted,subtracted = subtractFromInterval(amount,component)
            subtractedComponents.append(subtracted)
            amount = amount - amountSubtracted
            if leftOverInterval != "":
                leftOverComponents.append(leftOverInterval)
            if amount == 0:
                skip = True
        else:
            
            leftOverComponents.append(component)
    if len(leftOverComponents) > 0:
     
        return " ".join(leftOverComponents)," ".join(subtractedComponents)
    else:
        return ""," ".join(subtractedComponents)
def orderDict(myDict,myOrder):
    orderedDict = {}
    for key in myOrder:
        if dictHasKey(myDict,key):
            orderedDict[key]=myDict[key]
    return orderedDict
#this is used in reservations.py, maybe elsewhere
def mdhms(atd):
    import datetime
    def dhm(td):
        return {"months":td.days//30,"days":td.days%30, "hours":td.seconds//3600, "minutes":(td.seconds//60)%60}
    a_dhms = dhm(atd)
    a_dhms["seconds"] = atd.seconds - a_dhms["hours"]*3600 - a_dhms["minutes"]*60
    return a_dhms
def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def get_mdhms(timeString):
    import re
    import sys
    regEx=re.compile(".*(?:^|[ ])([0-9]+)month.*")
    match=regEx.match(timeString)
    months=int(match.groups()[0]) if not match == None else False
    regEx=re.compile(".*(?:^|[ ])([0-9]+)day.*")
    match=regEx.match(timeString)
    days=int(match.groups()[0]) if not match == None else False
    regEx=re.compile(".*(?:^|[ ])([0-9]{2,}):([0-9]{2,}):([0-9]{2,}).*")
    match=regEx.match(timeString)
    if match == None:
        print("Error, no time given in timeString: %s"%timeString)
        sys.exit(1)
    match=match.groups()
    hours=int(match[0])
    minutes=int(match[1])
    seconds=int(match[2])
    return (months,days,hours,minutes,seconds)
def get_seconds_absolute(mdhms):
    seconds = 0
    if mdhms[0] and mdhms[0]>0:
        seconds=mdhms[0] * DAYS_PER_MONTH * HOURS_PER_DAY * MINUTES_PER_HOUR * SECS_PER_MINUTE
    if mdhms[1] and mdhms[1] > 0:
        seconds+=mdhms[1] * HOURS_PER_DAY * MINUTES_PER_HOUR * SECS_PER_MINUTE
    seconds+=mdhms[2] * MINUTES_PER_HOUR * SECS_PER_MINUTE
    seconds+=mdhms[3] * SECS_PER_MINUTE
    seconds+=mdhms[4]
    return seconds


def comparePostOutJobs(input1,input2):
    import pandas as pd
    import numpy as np
    with open(input1,"r") as InFile:
        df1 = pd.read_csv(InFile,header=0)
    with open(input2,"r") as InFile:
        df2 = pd.read_csv(InFile,header=0)
    drop_cols=["MTBF","SMTBF","fixed-failures","Tc_Error","jitter"]
    if np.isnan(df1["delay"].values[0]):
        drop_cols.extend(["requested_time","cpu","delay","real_delay"])
    elif np.isnan(df1["cpu"].values[0]):
        drop_cols.extend(["requested_time","delay","cpu","real_cpu"])

    df1 = df1.drop(drop_cols,axis="columns")
    df2 = df2.drop(drop_cols,axis="columns")
    equal = True
    for i in df1:
        for j in range(0,len(df1[i].values),1):
            if df1[i].values[j] == df2[i].values[j]:
                continue
            else:
                equal = False
                break
        if not equal:
            break
    return equal


def compareMakespan(input1,input2):
    import pandas as pd
    with open(input1,"r") as InFile:
        df1 = pd.read_csv(InFile,header=0)
    with open(input2,"r") as InFile:
        df2 = pd.read_csv(InFile,header=0)
    drop_cols=["avg_pp_slowdown","avg-pp-slowdown","avg-pp-slowdown_dhms"]
    df1 = df1.drop(drop_cols,axis="columns")
    df2 = df2.drop(drop_cols,axis="columns")
    equal = True
    for i in df1:
        for j in range(0,len(df1[i].values),1):
            if df1[i].values[0] == df2[i].values[0]:
                continue
            else:
                equal = False
                break
        if not equal:
            break
    return equal
def sortJsonKeys(keys,keyOrder,default):
    ourKeys=[key for key in keys]
    
    ourNewKeys=[]
    for key in keyOrder:
        if ourKeys.count(key) == 1:
            ourKeys.remove(key)
            ourNewKeys.append(key)
   
    if default == "alphabetic":
        ourKeys.sort()
    elif default == "reverse_alphabetic":
        ourKeys.sort(reverse=True)
    ourNewKeys.extend(ourKeys)
    return ourNewKeys

#recursive function to count max levels of json
def countJsonLevels(ourJson):
    count=0
    if type(ourJson) == dict:
        for key in ourJson.keys():
            count=max(countJsonLevels(ourJson[key]),count)
        return count+1
    else:
        return 0
def sortJsonLevel(ourJson,levels,level,keyOrder,levelKeyOrders,default):
    import json
    #is this a leaf level?
    if type(ourJson) == dict:
        #no it is not a leaf level
        newJson=json.loads("{}")
        #do we sort this level?
        if level in levels:
            #yes we do
            #get our keyOrder ready
            keyOrderSort=keyOrder.copy()
          
            if dictHasKey(levelKeyOrders,str(level)):
                keyOrderSort=levelKeyOrders[str(level)]
            if dictHasKey(levelKeyOrders,f"+{level}"):
                keyOrderSort.extend(levelKeyOrders[f"+{level}"])

            ourKeys=sortJsonKeys(ourJson.keys(),keyOrderSort,default)
                
        else:
            ourKeys=ourJson.keys()
        #now the keys are in the right order for this level
        #set a new dict with appropriate values for each key
        for key in ourKeys:
            newJson[key]=sortJsonLevel(ourJson[key],levels,level+1,keyOrder,levelKeyOrders,default)
        return newJson
    else:
        return ourJson



        
# levels: The levels into the json you want to apply things to
#   IntervalSet ex: "1-3 6 9-11"
# keyOrder: The keys you want in a specific order for every level
#   List ex: ["age","name"]
# levelKeyOrders: The keys you want in a specific order for each level, clears keyOrder for that level
#                 If you want to add on to the keyOrder instead of clear it, add a plus to the level
#   Dict ex: {"1":["age","name"],"2":[]}
#        ex: {"+1":["age","name"],"2":[],"3":["length","width"]}        
# default: How to sort the rest of the keys
#   String.  Right now just "alphabetic" and "reverse_alphabetic"
        
def sortJson(ourJson,levelInterval="all",keyOrder=[],levelKeyOrders={},default="alphabetic"):
    import sys
    maxLevels=countJsonLevels(ourJson)
    if levelInterval == "all":
        levels=list(range(1,maxLevels+1,1))
    else:
        levels = getIntervalValues(levelInterval)
    if max(levels) > maxLevels:
        print(f"Error, sortJson: you included level {max(levels)} but the highest level is {maxLevels}")
        sys.exit(1)
    return sortJsonLevel(ourJson,levels,1,keyOrder,levelKeyOrders,default)

def applyKeyJsonSchema(value,schema,passedKeys):
    import sys
    import re
    global real_start
    global batsimOptions
    global batsimValues
    switchTypes={"bool":bool,"int":int,"string":str,"float":float,"object":dict,"none":None}
    iterateKeysToSkip=["type","required"]
    #lets get some info on the value for this key
    ourType=type(value)

    #Now lets figure out what this schema is all about
    #is it an array?  If so we need to find the correct schema
    if type(schema) == list:
        #it is.  iterate through and find the one that applies
        found=False
        for it_Schema in schema:
            if not dictHasKey(it_Schema,"type"):
                print(f"Error, applyKeyJsonSchema: no 'type' key in key: {'->'.join(f'{i}' for i in passedKeys)}")
                sys.exit(1)
            if switchTypes[it_Schema["type"]] == ourType:
                #do we need to regex check it?
                if (it_Schema["type"] == "string") and dictHasKey(it_Schema,"regex"):
                    #yes we do, let's check it
                    regEx=re.compile(it_Schema["regex"])
                    if not regEx.match(value):
                        #ok we didn't match
                        continue
                found = True
                applyKeyJsonSchema(value,it_Schema,passedKeys)
        if not found:
            print(f"Error, applyJsonSchema: no schema type matches. Key:{'->'.join(f'{i}' for i in passedKeys)} Type:{ourType}")
            sys.exit(1)
    #ok schema should be a schema we can work with
    #check if this represents a collection of keys or a value
    elif schema["type"] == "object":
        #ok it is a collection of keys, iterate over them
        for key in schema.keys():
            #only get the actual schema keys
            if key in iterateKeysToSkip:
                continue
            #ok this is a real schema key
            required = False
            #is this schema required?
            if dictHasKey(schema[key],"required"):
                required = schema[key]["required"]
            #ok if this key is required, make sure it is in config file
            if required and not dictHasKey(value,key):
                print(f"Error, applyKeyJsonSchema: schema says key:{'->'.join(f'{i}' for i in passedKeys+[key])} is required, but config file is missing it")
                sys.exit(1)
            applyKeyJsonSchema(value[key],schema[key],passedKeys+[key])
    else:
        #ok this schema is an actual value, let's check if we need to regex
        if (schema["type"] == "string") and dictHasKey(schema,"regex"):
            #yes we do, let's check it
            regEx=re.compile(schema["regex"])
            if not regEx.match(value):
                #ok we didn't match, put up an error
                print(f"Error, applyKeyJsonSchema: key: {'->'.join(f'{i}' for i in passedKeys)} did not match the regex of the schema")
                sys.exit(1)
        #ok get real_start,batsim,batsched values
        if dictHasKey(schema,"real_start"):
            print("real_start")
        if dictHasKey(schema,"batsim"):
            values=schema["batsim"]["values"]
            [v if v!="{}" else value for v in values]
            
        if dictHasKey(schema,"batsched"):
            print("batsched")
        

                

        
#keys "type","required","regex",real_start,batsim,batsched,xreal_start,xbatsim,xbatsched
#types "int","float","bool","string","none"

def applyJsonSchema(InConfig,InSchema):
    import sys
    
    #first go through all the keys of what we have
    for key in InConfig.keys():
        if not dictHasKey(InSchema,key):
            print(f"Error, applyJsonSchema: no key in schema. Key:{key}")
            sys.exit(1)
        applyKeyJsonSchema(InConfig[key],InSchema[key],[key])
        





