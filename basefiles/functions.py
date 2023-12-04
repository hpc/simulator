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
    with open(input1,"r") as InFile:
        df1 = pd.read_csv(InFile,header=0)
    with open(input2,"r") as InFile:
        df2 = pd.read_csv(InFile,header=0)
    if "cpu" in df1.columns:
        drop_cols=["requested_time","cpu"]
    elif "delay" in df1.columns:
        drop_cols=["requested_time","delay"]
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




