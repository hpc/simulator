"""
Usage:
    generate_grizzly_workload.py --time <string> --nodes <INT> [options]

Required Options:
    --time <string>                         The amount of time to include in the
                                            workload.  The format of this quoted string is:
                                            :                                   all data
                                            Month-Day-Year:                     from this date until end
                                            :Month-Day-Year                     from start until this date
                                            Month-Day-Year : Month-Day-Year     from this date to this date
    
    --nodes <INT>                           The amount of nodes this workload will be using 

Optional Options:
    -i <FILE> --input <FILE>                The grizzly_data csv file
                                            [default: ./sanitized_jobs.csv]
    --number-of-jobs INT                    The number of jobs wanted from the start.If negative,
                                            it is the amount
                                            of jobs from the end going backward.If not specified,
                                            all jobs in the time range are included.
    
    -o <FILE> --output <FILE>               Where to output the workload
                                            [default: ./grizzly_workload.json]

    --random-selection                      To get a random selection of jobs. '--number-of-jobs'
                                            needs to be set for this option.

    --timestamp-out                         Add the grizzly time to the end of the name of the output

    --random-submissions                    will generate random submissions using
                                            '--submission' option as mean time between them
                                            with exponential distribution

    --submission-time <FLOAT><:exp|fixed>   This dictates the time between submissions and what kind of randomness.
                      <FLOAT:FLOAT:unif>    If zero is used for a float,combined with ":fixed" then all jobs will start at time zero.
                                            If omitted, grizzly data will be used.
                                                    
                                            exp: This will be exponentially distributed, random values with mean time between submissions to be FLOAT.
                                            fixed: All jobs will have this time between them unless zero is used for a FLOAT.
                                            unif: This will be uniform, random values from min:max
                                            ex:     
                                                    '--submission-time "200.0:exp"'
                                                    '--submission-time "100.0:fixed"'
                                                    '--submission-time "0.0:fixed"'
                                                    '--submission-time "0:200.0:unif"'
                                                                                   
    --wallclock-limit <FLOAT|INT%|STR>      wallclock limits will all be set to this for FLOAT. (-1) means the value will not be used in Batsim.
                                            wallclock limits will be a % of run time for INT%
                                            wallclock limits will be random from min % of runtime to max % in STR format '"min%:max%"'
                                            wallclock limits will be random seconds from min to max in STR format  '"min:max"'
                                            wallclock limits will be what the grizzly data is if not set.
                                            ex:     '--wallclock-limit -1'
                                                    '--wallclock-limit 500.3'
                                                    '--wallclock-limit 101%'
                                                    '--wallclock-limit "50%:150%"'
                                                    '--wallclock-limit "100:3000"'

    --read-time <FLOAT|INT%|STR>            set this fixed time to readtime in seconds for FLOAT.
                                            set this to % of run time for INT%.
                                            set this to random % of run time for STR format "min%:max%"
                                            set this to random seconds from min to max in STR format   "min:max".
                                            readtime will be omitted in the workload if not included.
                                            ex:     '--read-time 20'
                                                    '--read-time 2%'
                                                    '--read-time "2%:4%"'
                                                    '--read-time "2:20"'

    --dump-time <FLOAT|INT%|STR>            set this fixed time to dumptime in seconds for FLOAT.
                                            set this to % of run time for INT%.
                                            set this to random % of run time for STR format "min%:max%"
                                            set this to random seconds from min to max in STR format   "min:max".
                                            dumptime will be omitted in the workload if not included.
                                            ex:     '--dump-time 20'
                                                    '--dump-time 3%'
                                                    '--dump-time "3%:5%"'
                                                    '--dump-time "3:30"'

    --checkpoint-interval <FLOAT|INT%|STR>  set this fixed time to checkpoint in seconds for FLOAT.
                                            set this to % of run time for INT%.
                                            set this to random % of run time for STR format "min%:max%"
                                            set this to random seconds from min to max in STR format   "min:max".
                                            checkpoint will be omitted in the workload if not included.
                                            ex:     '--checkpoint-interval 120'
                                                    '--checkpoint-interval 30%'
                                                    '--checkpoint-interval "10%:30%"'
                                                    '--checkpoint-interval "120:240"'
"""


from docopt import docopt,DocoptExit
import pandas as pd
import numpy as np
import os
import sys
import json

def parseTimeString(aTimeStr,durations_times,newSize):
    # if there is a colon (:)
    times=[]
    if not aTimeStr.find(":") == -1:
        minMax = aTimeStr.split(":")
        #if there are %'s and a colon
        if not minMax[0].find("%")== -1 and not minMax[1].find("%")== -1:
            minPercent = int(minMax[0].rstrip("%"))
            maxPercent = int(minMax[1].rstrip("%"))
            percents = (np.random.randint(low=minPercent,high=maxPercent+1,size=newSize))/100
            times = percents * durations_times
            times = np.ceil(times)
        # != is the same as xor. if only one has a % but there is a colon
        elif (not minMax[0].find("%")==-1) != (not minMax[1].find("%")==-1):
            print("you provided a random string from min:max but one had a percent sign and the other didn't")
            print(aTimeStr)
            sys.exit(1)
        # only a colon
        else:    
            times = np.random.randint(low=int(minMax[0]),high=int(minMax[1])+1,size=newSize)
    # only a percent
    elif not aTimeStr.find("%")== -1:
        percent = int(aTimeStr.rstrip("%"))
        for time in durations_times:
            times.append(np.ceil(time*(percent/100)))
    # only a float
    else:
        time = float(aTimeStr)
        times = [time] * newSize
    return times

def parseSubmissionTime(aTimeStr,newSize):
    # if there is a colon (:)
    times=[]
    if not aTimeStr.find(":") == -1:
        STR = aTimeStr.split(":")
        #check if a uniform randomness
        if len(STR) == 3:
            if not STR[2].find("unif")== -1:
                times = np.random.uniform(low=float(STR[0]),high=float(STR[1]),size=newSize)
                times[0] = 0
                times = np.cumsum(times)
        #check if fixed or exp
        elif len(STR)==2:
            if not STR[1].find("fixed")== -1:
            
                time = float(STR[0])
                if time == 0:
                    times = [0] * newSize
                else:
                    times = [time] * newSize
                    times[0]=0
                    times = np.cumsum(times)
            elif not STR[1].find("exp"):
                times = np.random.exponential(float(STR[0]),newSize)
                times[0]=0
                times=np.cumsum(times)
    if len(times) == 0:
        print("you provided a String for --submission-time in the wrong format")
        print(aTimeStr)
        sys.exit(1) 
    return times



try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

#Required
timeString = args["--time"]
nodes = int(args["--nodes"])

#Optional
inputFile = args["--input"]
submission = args["--submission-time"] if args["--submission-time"] else False
timeStampOut = True if args["--timestamp-out"] else False
outputFile = args["--output"]
randomSelection = args["--random-selection"]
randomSubmissions = True if args["--random-submissions"] else False
readTime = args["--read-time"] if args["--read-time"] else False
dumpTime = args["--dump-time"] if args["--dump-time"] else False
checkpointTime = args["--checkpoint-interval"] if args["--checkpoint-interval"] else False
wallclockLimit = args["--wallclock-limit"] if args["--wallclock-limit"] else False
numberOfJobs = int(args["--number-of-jobs"]) if args["--number-of-jobs"] else False

#parse timeString
times = timeString.split(":",1)
startStrings = times[0].split("-",2)
endStrings = times[1].split("-",2)
noStart = False
noEnd = False
if not len(startStrings) == 3:
    noStart = True
else:
    startM = int(startStrings[0])
    startD = int(startStrings[1])
    startY = int(startStrings[2])
if not len(endStrings) == 3:
    noEnd = True
else:
    endM = int(endStrings[0])
    endD = int(endStrings[1])
    endY = int(endStrings[2])


#Now lets get our grizzly data and make a json out of it

#first import the data
df = pd.read_csv(inputFile,sep=",",header=0)

#get rid of data based on submit time and the --time option
df.submit_time=pd.to_datetime(df.submit_time)
df=df.sort_values(by='submit_time')

#needed to set these after we read in the data
size = len(df)

if noStart:
    startM = df["submit_time"].iloc[0].month
    startD = df["submit_time"].iloc[0].day
    startY = df["submit_time"].iloc[0].year
if noEnd:
    endM = df["submit_time"].iloc[size-1].month
    endD = df["submit_time"].iloc[size-1].day
    endY = df["submit_time"].iloc[size-1].year

#make outfile if timeStampOut
if timeStampOut:
    tmp = outputFile.rsplit(".",1)
    outputFile = tmp[0] + "_{startM}-{startD}-{startY}__{endM}-{endD}-{endY}.{ext}".format(
                    startM=startM,startD=startD,startY=startY,endM=endM,endD=endD,endY=endY,ext=tmp[1])

# still getting rid of data based on --time option
# since we are not taking time-of-day into consideration, make sure start_time has 00:00:00 and end_time is 23:59:59                    
start_time_str = "{startY}-{startM}-{startD} 00:00:00".format(startY=startY,startM=str(startM).zfill(2),startD=str(startD).zfill(2))
end_time_str = "{endY}-{endM}-{endD} 23:59:59".format(endY=endY,endM=str(endM).zfill(2),endD=str(endD).zfill(2))

start_time = pd.to_datetime(start_time_str)
end_time = pd.to_datetime(end_time_str)

df=df.loc[df.submit_time >= start_time]
df=df.loc[df.submit_time <= end_time]

if not type(numberOfJobs)==bool and not randomSelection:
    if not numberOfJobs == 0: 
        if numberOfJobs<0:
            df=df.tail(n=abs(numberOfJobs))
        else:
            df=df.head(n=(numberOfJobs))
            

# finished getting rid of data, record our new size
newSize = len(df)

#if random-selection, you must input number of jobs.
if randomSelection and not type(numberOfJobs)==bool:
    df = df.iloc[np.random.randint(low=0,high=newSize,size=numberOfJobs)]
    # the index has duplicates because we might be getting the same row more than once
    # so we reset the index to be a list from 0 to numberOfJobs
    df.index=list(range(0,numberOfJobs,1))
    ids=df["jobid"].astype(str)
    ids = [ids[i]+"_"+str(i) for i in df.index]
    df["jobid"]=ids
    newSize=len(df)
    
    
elif randomSelection and type(numberOfJobs)==bool:
    print("you need random selection but you did not specify the number of jobs using the --number-of-jobs option")
    sys.exit(1)

# set our submit times
if type(submission) == bool:
    #convert submit times to integers starting at time 0
    subtract = df.submit_time.min()
    df.sort_values(by="submit_time",axis=0,inplace=True)
    df.index = range(0,newSize,1)
    submits_times = df.submit_time-subtract
    submits = submits_times.values.astype('int')
    submits = (submits/10**9).astype('int')
else:
    submits = parseSubmissionTime(submission,newSize)
    

# convert endtime - starttime to durations
durations_times=((df["end_time"].astype("datetime64[ns]")-df["start_time"].astype("datetime64[ns]"))/10**9).astype('int')

resources=df["req_nodes"]

ids=df["jobid"].astype('str')

walltimes=df["wallclock_limit"]
cols=[ids,submits,resources,ids]
column_names=["id","subtime","res","profile"]
if wallclockLimit:
    walltimes = parseTimeString(wallclockLimit,durations_times,newSize)
cols.append(walltimes)
column_names.append("walltime")
if readTime:
    readtimes = parseTimeString(readTime,durations_times,newSize)
    cols.append(readtimes)
    column_names.append("readtime")
if dumpTime:
    dumptimes = parseTimeString(dumpTime,durations_times,newSize)
    cols.append(dumptimes)
    column_names.append("dumptime")
if checkpointTime:
    checkpoint = parseTimeString(checkpointTime,durations_times,newSize)
    cols.append(checkpoint)
    column_names.append("checkpoint")


data=list(zip(*cols))
jobs=pd.DataFrame(data=data,columns=column_names)

profileTypes=ids
types=["delay"]*newSize
delay=durations_times

data=list(zip(types,delay,delay))
profiles=pd.DataFrame(data=data,columns=["type","delay","real_delay"],index=profileTypes)

profiles2dict=profiles.to_dict(orient="index")
jobs2dict=jobs.to_dict(orient="records")

jsonData={"nb_res":nodes,"jobs":jobs2dict,"profiles":profiles2dict}
with open(outputFile, 'w') as outfile:
    json.dump(jsonData, outfile,indent=4)
