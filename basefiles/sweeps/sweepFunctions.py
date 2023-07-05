__all__=["dictHasKey","blockSize","expandTotalTime","myDebug"]
import re
import sys


def blockSize(id,p,n,function=int):
    def Block_low(id,p,n):
        import numpy as np
        return np.floor(id*n/float(p))
    def Block_high(id,p,n):
        return Block_low(id+1,p,n) -1

    return function(Block_high(id,p,n)-Block_low(id,p,n) +1)

def myDebug(msg=""):
    print(f"Debug {sys._getframe().f_back.f_lineno}: {msg}")

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def parseTime(time):
    import re
    import sys

    # if isinstance(idString,list):
    #     return idString
    # regEx=re.compile(".*(\[[0-9,]+\]).*")
    # match=regEx.match(idString)
    # #does the idString match a range type of String   ie  [1,3,4]
    # if match:
    #     #yes it does
    #     return idString.strip("][").split(",")
    # else:
    #     # ok so we don't have a list we have a range  ie  2;10;2     2 to 10(inclusive) by 2's
    #     aMin,aMax,aStep = idString.split(";")
    #     if aMin and aMax and aStep:
    #         aMin=int(aMin)
    #         aMax=int(aMax)
    #         aStep=int(aStep)
    #         return list(range(aMin,aMax+aStep,aStep))
    #     else:
    #         print("Error 'workload-ids' is invalid")
    #         sys.exit(1)


def parseRandomTime(timeString):
    import re
    import sys
    regEx=re.compile(".*(?:^|[ ])[\[]([0-9;, ]+)[\]]month.*")
    match=regEx.match(timeString)
    months=match.groups()[0] if not match == None else False
    regEx=re.compile(".*(?:^|[ ])[\[]([0-9;, ]+)[\]]day.*")
    match=regEx.match(timeString)
    days=match.groups()[0] if not match == None else False
    regEx=re.compile(".*(?:^|[ ])[\[]([0-9;, ]+)[\]]:[\[]([0-9;, ]+)[\]]:[\[]([0-9;, ]+)[\]].*")
    match=regEx.match(timeString)
    match=match.groups()
    hours=match[0]
    minutes=match[1]
    seconds=match[2]
    return (months,days,hours,minutes,seconds)
def expandTime(time):
    if time == False:
        return [False]
    if not time.find(";") == -1:
        #ok we found a min,max,step
        min,max,step = time.split(";")
        return list(range(int(min),int(max)+int(step),int(step)))
    else:
        return [int(i) for i in time.split(",")]
def expandTotalTime(mdhms):
    import re
    import sys
    mdhms = parseRandomTime(mdhms)
    mdhms = tuple([i.strip("[] ") if i!=False else False for i in mdhms])
    m=expandTime(mdhms[0]) if mdhms[0] != False else [False]
    d=expandTime(mdhms[1]) if mdhms[1] != False else [False]
    h=expandTime(mdhms[2]) if mdhms[2] != False else [0]
    min=expandTime(mdhms[3]) if mdhms[3] != False else [0]
    s=expandTime(mdhms[4]) if mdhms[4] != False else [0]
    maxSize = 0
    for i in [m,d,h,min,s]:
        maxSize = max(maxSize,len(i))
    times = []
    count = 0
    countTrans = ["months","days","hours","minutes","seconds"]
    for i in [m,d,h,min,s]:
        if len(i) < maxSize:
            if len(i) == 1 :
               
               times.append(i*(maxSize)) 
            else:
                print(f"Error with {countTrans[count]}: {i}")
                print(f"you provided a range that translates to a smaller amount of values than the largest of values: size:{len(i)}, largest:{maxSize}")
                
                sys.exit()
        else:
            times.append(i)
        count+=1
    stringTimes = []
    for i in range(0,maxSize,1):
        m= "" if times[0][i] == False else f"{times[0][i]}months "
        d= "" if times[1][i] == False else f"{times[1][i]}days "
        stringTimes.append(f"{m}{d}{times[2][i]:02}:{times[3][i]:02}:{times[4][i]:02}")
    return stringTimes
