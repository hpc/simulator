__all__=["dictHasKey","blockSize"]

MONTH_DAYS=[31,28,31,30,31,30,31,31,30,31,30,31]
SECS_PER_MINUTE=60
MINUTES_PER_HOUR=60
HOURS_PER_DAY=24
DAYS_PER_MONTH=30
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    import re
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

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

batsimOptions={}
batschedOptions={}
realStartOptions={}
batsimCMD=""
batschedCMD=""
def getRealStartOptions(CMD,schema,value):
    global realStartOptions
    #get all key/value pairs in real_start list
    for kv in schema[CMD]:
        key,schema_value=kv.popitem()
        #add the appropriate key/value to globals
        if schema_value=="{}":
            schema_value=value
        realStartOptions[key]=schema_value
def getCMDOptions(CMD,Options,schema,value):
    #get all key/value optional_multi_key/value in batsim list
    for kvo in schema[CMD]:
        multiple=False
        if dictHasKey(kvo,"multiple"):
            multiple=kvo.pop("multiple")
        key,schema_value=kvo.popitem()
        if schema_value == "{}":
            schema_value = value
        tmp=None
        if dictHasKey(Options,key):
            #ok we already have this key, can we have multiple?
            if multiple:
                #yes we can, add it as a list
                tmp=Options[key]
                tmp.append(schema_value)
            else:
                #ok we can't have multiple, ignore it
                continue
        else:
            #ok we do not already have this key
            tmp=[schema_value]
        #so now tmp is what this key should have as a value, set it
        Options[key]=tmp.copy()
    return Options
def applyKeyJsonSchema(value,schema,passedKeys):
    import sys
    import re
    global batsimOptions
    global batschedOptions
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
            #is this schema required?
            required = schema[key]["required"] if dictHasKey(schema[key],"required") else False
            #ok if this key is required, make sure it is in config file
            if required and not dictHasKey(value,key):
                print(f"Error, applyKeyJsonSchema: schema says key:{'->'.join(f'{i}' for i in passedKeys+[key])} is required, but config file is missing it")
                sys.exit(1)
            applyKeyJsonSchema(value[key],schema[key],passedKeys+[key])
    elif schema["type"] == "ignore":
        return
    else:
        #ok this schema is an actual value, let's check the config value type against the schema type
        if (switchTypes[schema["type"]] == ourType) or ((switchTypes[schema["type"]] == float ) and (ourType == int)):
            #ok let's see if we need to regex it
            if (schema["type"] == "string") and dictHasKey(schema,"regex"):
                #yes we do, let's check it
                regEx=re.compile(schema["regex"])
                if not regEx.match(value):
                    #ok we didn't match, put up an error
                    print(f"Error, applyKeyJsonSchema: key: {'->'.join(f'{i}' for i in passedKeys)} did not match the regex of the schema")
                    sys.exit(1)
            #ok get real_start,batsim,batsched values
            if dictHasKey(schema,"real_start"):
                getRealStartOptions("real_start",schema,value)
            if dictHasKey(schema,"true_real_start"):
                if value == True:
                    getRealStartOptions("true_real_start",schema,value)
            if dictHasKey(schema,"false_real_start"):
                if value == False:
                    getRealStartOptions("false_real_start",schema,value)
            if dictHasKey(schema,"batsim"):
                batsimOptions=getCMDOptions("batsim",batsimOptions,schema,value)
            if dictHasKey(schema,"true_batsim"):
                if value == True:
                    batsimOptions=getCMDOptions("true_batsim",batsimOptions,schema,value)    
            if dictHasKey(schema,"false_batsim"):
                if value == False:
                    batsimOptions=getCMDOptions("false_batsim",batsimOptions,schema,value)
            if dictHasKey(schema,"batsched"):
                batschedOptions=getCMDOptions("batsched",batschedOptions,schema,value)
            if dictHasKey(schema,"true_batsched"):
                if value == True:
                    batschedOptions=getCMDOptions("true_batsched",batschedOptions,schema,value)
            if dictHasKey(schema,"false_batsched"):
                if value == False:
                    batschedOptions=getCMDOptions("false_batsched",batschedOptions,schema,value)
        else:
            print(f"Error, applyKeyJsonSchema: key: {'->'.join(f'{i}' for i in passedKeys)} did not match any of the available types")
            sys.exit(1)
#apply items that did not show up in config that have a none type in schema
def applyNone(schema,InConfig,passedKeys):
    import sys
    global batsimOptions
    global batschedOptions
    iterateKeysToSkip=["type","required"]
    #we are only concerned with lists in the schema
    #if it is a list check for none
    if type(schema) == list:
        for tmp_schema in schema:
            if dictHasKey(tmp_schema,"type"):
                if tmp_schema["type"] == "none":
                    #ok we have a type == none, lets check if InConfig has this key
                    config=InConfig
                    for key in passedKeys:
                        if dictHasKey(config,key):
                            config=config[key]
                            continue
                        else:
                            #the key was not found, apply the none
                            #first check if it was required
                            if dictHasKey(tmp_schema,"required"):
                                if tmp_schema["required"] == True:
                                    print(f"Error, applyNone: schema says key:{'->'.join(f'{i}' for i in passedKeys)} is required, but config file is missing it")
                                    sys.exit(1)
                            #ok it was not required, we can apply the none
                            if dictHasKey(tmp_schema,"real_start"):
                                getRealStartOptions("real_start",tmp_schema,"")
                            if dictHasKey(tmp_schema,"batsim"):
                                batsimOptions = getCMDOptions("batsim",batsimOptions,tmp_schema,"")
                            if dictHasKey(tmp_schema,"batsched"):
                                batschedOptions = getCMDOptions("batsched",batschedOptions,tmp_schema,"")
                            break
                    #if we found our none we can now break
                    break
            else:
                print(f"Error, applyNone: no 'type' key in key: {'->'.join(f'{i}' for i in passedKeys)}")
                sys.exit(1)
    else:
        #it is not a list, but if it is an object, it may contain a list
        if dictHasKey(schema,"type"):
            if schema["type"] == "object":
                #it is an object, however it only makes sense to check the none's in this object if the config has this outer key
                config=InConfig
                for key in passedKeys:
                    if dictHasKey(config,key):
                        config=config[key]
                        continue
                    else:
                        #ok, we don't have this object in our config so we don't have to process any none's inside this object
                        return
                #so we DO have this object in our config.  Iterate the keys of the object and applyNone to each legitimate key
                for key in schema.keys():
                    #only get the actual schema keys
                    if key in iterateKeysToSkip:
                        continue
                    applyNone(schema[key],InConfig,passedKeys+[key])
            else:
                #ok, it is not a list and not an object.  It is impossible for this key to have any "none"s
                return
        else:
            print(f"Error, applyNone: no 'type' key in key: {'->'.join(f'{i}' for i in passedKeys)}")
            sys.exit(1)
def populateCMDs():
    global batsimCMD
    global batschedCMD
    global batsimOptions
    global batschedOptions
    #lets start with our base case
    batsimCMD = f" -s {batsimOptions.pop('-s')[0]} -p {batsimOptions.pop('-p')[0]} -w {batsimOptions.pop('-w')[0]} -e {batsimOptions.pop('-e')[0]}"
    batsimCMD += " --disable-schedule-tracing --disable-machine-state-tracing"
    #ok let's add to it
    while len(batsimOptions) > 0:
        key,v_list=batsimOptions.popitem()
        for value in v_list:
            if value != "":
                batsimCMD += f" {key} {value}"
            else:
                batsimCMD += f" {key}"
    #lets start with our base case
    batschedCMD = f" -v {batschedOptions.pop('-v')[0]} -s {batschedOptions.pop('-s')[0]} --verbosity {batschedOptions.pop('--verbosity')[0]}"
    #ok let's add to it
    while len(batschedOptions) > 0:
        key,v_list=batschedOptions.popitem()
        for value in v_list:
            if value != "":
                batschedCMD += f" {key} {value}"
            else:
                batschedCMD += f" {key}"

        
#keys "type","required","regex",real_start,batsim,batsched,xreal_start,xbatsim,xbatsched
#types "int","float","bool","string","none"

def applyJsonSchema(InConfig,InSchema):
    import sys
    import re
    resv_regEx=re.compile("^reservations[-](?!start)")
    #first go through all the keys of what we have
    for key in InConfig.keys():
        if resv_regEx.match(key) != None:
            key = "reservations-"
        if not dictHasKey(InSchema,key):
            print(f"Error, applyJsonSchema: no key in schema. Key:{key}")
            sys.exit(1)
        applyKeyJsonSchema(InConfig[key],InSchema[key],[key])
    for key in InSchema.keys():
        applyNone(InSchema[key],InConfig,[key])
    #We've taken care of objects that have required keys, lists that have type none but required
    #all that is left are required keys in the main keys
    for key in InSchema.keys():
        required=False
        #first make sure we aren't dealing with a list
        if type(InSchema[key]) == list:
            continue
        if dictHasKey(InSchema[key],"required"):
            required = InSchema[key]["required"]
        #only need to check config if required is True
        if required:
            #ok, we do need to check
            if not dictHasKey(InConfig,key):
                #uh-oh, we don't have that key, yet it is required
                print(f"Error, applyJsonSchema: schema says key:{key} is required, but config file is missing it")
                sys.exit(1)
    #ok lets populate our commands
    populateCMDs()
    return
        





