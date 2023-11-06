import machines as mach
import json
import pandas as pd
import functions
from copy import deepcopy
import datetime
import numpy as np

MONTH_DAYS=[31,28,31,30,31,30,31,31,30,31,30,31]
SECS_PER_MINUTE=60
MINUTES_PER_HOUR=60
HOURS_PER_DAY=24
DAYS_PER_MONTH=30



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
# def get_seconds_start(mdhms):
#     myAdd = 1
        
#     seconds = 0
#     if mdhms[0] and mdhms[0]>myAdd:
#         seconds=sum(MONTH_DAYS[:mdhms[0]-myAdd])
#     if mdhms[1] and mdhms[1] > myAdd:
#         seconds+=(mdhms[1]-myAdd) * HOURS_PER_DAY * MINUTES_PER_HOUR * SECS_PER_MINUTE
#     seconds+=mdhms[2] * MINUTES_PER_HOUR * SECS_PER_MINUTE
#     seconds+=mdhms[3] * SECS_PER_MINUTE
#     seconds+=mdhms[4]
#     return seconds
# def get_seconds_absolute(mdhms):
#     seconds = 0
#     if mdhms[0] and mdhms[0]>myAdd:
#         seconds=sum(MONTH_DAYS[:mdhms[0]-myAdd])
#     if mdhms[1] and mdhms[1] > myAdd:
#         seconds+=(mdhms[1]-myAdd) * HOURS_PER_DAY * MINUTES_PER_HOUR * SECS_PER_MINUTE
#     seconds+=mdhms[2] * MINUTES_PER_HOUR * SECS_PER_MINUTE
#     seconds+=mdhms[3] * SECS_PER_MINUTE
#     seconds+=mdhms[4]
#     return seconds

#  "reservations-resv1":
#             {
#                 "reservations-array":
#                 [
#                     
#                       {
#                         "subdivisions":128,      <---- not to be used with randomness in intervals
#                         "subdivisions-unit":"1month 0days 00:00:00",   <----not to be used with randomness in intervals
#                         "type":"parallel_homogeneous",
#                         "machines":
#                         {
#                             "prefix":"a",
#                             "machine-speed":1,
#                             "total-resources":"0-1489",
#                             "interval":"0-1489"
#                         },
#                         "repeat-every":"1months 0days 00:00:00",
#                         "time":"09:00:00",
#                         "start":"1months 0days 12:00:00",
#                         "submit":-1,
#                         "count":30
#                     }
#                 ]
#             },

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
def generate_reservations(reservations_json):
    ourJson={}
    if isinstance(reservations_json,dict):
        ourJson=json.loads(json.dumps(reservations_json))
    else:
        ourJson=json.loads(reservations_json)
    reservationJson=ourJson["reservations-array"]
    ourArray = []



    #first check if we need to auto-generate more reservations
    resvCount=0
    for resv in reservationJson:
        print(resv)
        subdivisions = int(resv["subdivisions"]) if dictHasKey(resv,"subdivisions") else False
        subdivisionsUnit = resv["subdivisions-unit"] if dictHasKey(resv,"subdivisions-unit") else False
        
        if (subdivisions == False) or (subdivisions == 1) :
            #ok we don't need to generate reservations for this one
            #add it to the ourArray as-is after adding its order number
            resv["order"]=resvCount
            ourArray.append(deepcopy(resv))

        else:
            #ok we do need to auto-generate more reservations
            #get parts of the reservation json
            machinesJson=resv["machines"]
            resvType=resv["type"]
            speed = machinesJson['machine-speed'] if dictHasKey(machinesJson, "machine-speed") else False
            nb_reservations=resv["count"] if dictHasKey(resv, "count") else 1
            repeatEvery=resv["repeat-every"] if dictHasKey(resv,"repeat-every") else False
            #required options
            time=resv["time"]
            start=resv["start"]
            submitBeforeStart=resv["submit-before-start"] if dictHasKey(resv,"submit-before-start") else False
            submit=resv["submit"] if dictHasKey(resv,"submit") else False
            

            #ok lets use the original interval to find how many total nodes to use
            ourInterval = machinesJson["interval"]
            machinesTotal = functions.countTotalInterval(ourInterval)
            start_mdhms = get_mdhms(start)
            start_totalSeconds = get_seconds_absolute(start_mdhms)
            my_mdhms = get_mdhms(subdivisionsUnit)
            totalSecondsUnit = get_seconds_absolute(my_mdhms)
    
            secondsPerType = np.floor(totalSecondsUnit/subdivisions)
            for currentType in range(1,subdivisions+1,1):
                nodesInType = functions.blockSize(currentType-1,subdivisions,machinesTotal)
                aType = {}
                aType["type"] = resvType
                aType["machines"] = deepcopy(machinesJson)
                if not repeatEvery == False:
                    aType["repeat-every"] = repeatEvery
                aType["time"] = time
                
                ourInterval,usedInterval = functions.subtractFromTotalInterval(nodesInType,ourInterval)
                aType["machines"]["interval"]=usedInterval
                totalSeconds = start_totalSeconds +(secondsPerType * (currentType-1))
                myTime = functions.mdhms(datetime.timedelta(seconds = totalSeconds))
                aType["start"] = f"{myTime['months']}months {myTime['days']}days {myTime['hours']:02}:{myTime['minutes']:02}:{myTime['seconds']:02}"        
                if submitBeforeStart != False:
                    aType["submitBeforeStart"] = submitBeforeStart
                else:    
                    aType["submit"] = submit
                aType["count"] = nb_reservations
                aType["order"]=resvCount
                
                ourArray.append(deepcopy(aType))
        resvCount+=1
            
    #ok we auto-generated any reservations we may need
    #now process them like all reservations          
                  
    ourArray = json.loads(json.dumps(ourArray))
    jobs=[]
    profiles={}
    idStart=1
    for resv in ourArray:
        ids=[]
        types=[]
        profileTypes=[]
        starts=[]
        durations=[]
        submits=[]
        allocs=[]
        orders=[]
        #get parts of the reservation json
        order=resv["order"]
        machinesJson=resv["machines"]
        resvType=resv["type"]
        speed = machinesJson['machine-speed'] if dictHasKey(machinesJson, "machine-speed") else False
        nb_reservations=int(resv["count"]) if dictHasKey(resv, "count") else 1
        repeatEvery=resv["repeat-every"] if dictHasKey(resv,"repeat-every") else False
        #required options
        time=resv["time"]
        start=resv["start"]
        submitBeforeStart=resv["submit-before-start"] if dictHasKey(resv,"submit-before-start") else False
        submit=resv["submit"] if dictHasKey(resv,"submit") else False
        
        #populate some of our lists
        ids=list(range(idStart,nb_reservations+idStart,1))
        ids=[str(i) for i in ids]
        profileTypes=ids
        types=[resvType]*nb_reservations
        orders=[order]*nb_reservations
        
        #change the start of the ids that will be used in the next iteration of our loop
        idStart+=nb_reservations
        
        #get the machines that reservations will run on
        resources = mach.parse_machines_json(machinesJson, nb_reservations) if dictHasKey(machinesJson, "resources") else False
        intervals = mach.parse_machines_json(machinesJson, nb_reservations) if dictHasKey(machinesJson, "interval") else False
        
          
        #convert the month_day_hour_minute_second fields into their components
        time_mdhms = get_mdhms(time)
        start_mdhms = get_mdhms(start)
        submitBeforeStart_mdhms = get_mdhms(submitBeforeStart) if submitBeforeStart else False
        submit_mdhms = False
        if submit and submit == -1:
            submits=[0] * nb_reservations
        elif submit:
            submit_mdhms = get_mdhms(submit)
            
        
        repeatEvery_mdhms = get_mdhms(repeatEvery) if repeatEvery else False
        
        #change the m_d_h_m_s components into seconds
        start_seconds=get_seconds_absolute(start_mdhms)
        time_seconds = get_seconds_absolute(time_mdhms)
        repeatEvery_seconds=get_seconds_absolute(repeatEvery_mdhms) if repeatEvery else False
        submitBeforeStart_seconds=get_seconds_absolute(submitBeforeStart_mdhms) if submitBeforeStart else False
        submit_seconds=get_seconds_absolute(submit_mdhms) if submit and not submit==-1 else False
        
        
        
        
        for i in range(1,nb_reservations+1,1):
            if i == 1:
                starts=[start_seconds]
                if submitBeforeStart:
                    submit_time = start_seconds - submitBeforeStart_seconds
                    if submit_time > -1:
                        submits=[submit_time]
                    else:
                        submits=[0]
                elif not submit == -1:
                    submits=[submit_seconds]
                    
            else:
                aStart = start_seconds+(repeatEvery_seconds*(i-1))
                starts.append(aStart)
                if submitBeforeStart:
                    submit_time = aStart - submitBeforeStart_seconds
                    if submit_time > -1:
                        submits.append(submit_time)
                    else:
                        submits.append(0)
                elif not submit == -1:
                    submits.append(submit_seconds)
        cols=[]
        column_names=[]
        purposes=["reservation"]*nb_reservations
        durations = [time_seconds]*nb_reservations
        # add one second to each walltime for the case when call_me_later has a latency
        walltimes = [dur+1 for dur in durations]
        if intervals:
            allocs=intervals[0]
            resources=intervals[1]
            cols=[ids,submits,resources,ids,allocs,starts,walltimes,purposes,orders]
            column_names=["id","subtime","res","profile","alloc","start","walltime","purpose","order"]
        else:
            resources=resources[0]
            cols=[ids,submits,resources,ids,starts,walltimes,purposes,orders]
            column_names=["id","subtime","res","profile","start","walltime","purpose","order"]
            #set the required columns
        
        
            #first get all the columns of jobs into a list and then make a dataframe out of it
        data=list(zip(*cols))
        jobs_df=pd.DataFrame(data=data,columns=column_names)
        
            #change the name of durations to make more sense of the json file
        delay=durations
        real_delay=delay
        profiles_df=pd.DataFrame()
        if resvType == "delay":
                #now get all the columns of profiles into a list and then make a dataframe out of it. notice the index
                #of the dataframe will have the profileTypes as its index.  Read why below.
            data=list(zip(types,delay,real_delay))
        
            profiles_df=pd.DataFrame(data=data,columns=["type","delay","real_delay"],index=profileTypes)
        else:
                #convert times to cpu
            delay = [duration * speed for duration in durations]
            real_delay = delay
            com = [0] * nb_reservations
            
            data=list(zip(types,delay,com,real_delay))
            profiles_df=pd.DataFrame(data=data,columns=["type","cpu","com","real_cpu"],index=profileTypes)
            
            
            
        
            #convert the dataframes to dictionaries,notice "orient" is "index" for profiles and "records" for jobs
            #This is because profiles are a list of dict of dicts whereas jobs are just a series of dicts
            #ie profiles 
            #       {"job_id_number1":{"type":"delay","delay":200,"real_delay":200},"job_id_number2":{...}}
            #vs jobs
            #       [{"option":value,"option":value,...},{"option":value,"option":value,...}]
        profiles2dict=profiles_df.to_dict(orient="index")
        jobs2dict=jobs_df.to_dict(orient="records")
       
        profiles.update(profiles2dict)
        jobs.extend(jobs2dict)
    return (jobs,profiles)  
