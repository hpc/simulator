"""
A program to generate a synthetic workload for Batsim Simulator

Usage: 
    generate_synthetic_workload.py --help [<type-of-info>]
    generate_synthetic_workload.py -F FILE
    generate_synthetic_workload.py --number-of-jobs INT --nodes INT  --number-of-resources STR --duration-time STR --submission-time STR 
                                    [--scaleTimeWidth INT]
                                    [--output FILE]
                                    [--wallclock-limit <FLOAT|INT%|STR>]
                                    [--read-time <FLOAT|INT%|STR>] [--dump-time <FLOAT|INT%|STR>]
                                    [--checkpoint-interval <FLOAT|INT%|STR>]

Arguments:
    FILE                                            an absolute location to a file
    PATH                                            an absolute location to a directory
    INT                                             an integer
    FLOAT                                           a decimal number
    STR                                             a string of characters
Required Options 1:
    --help                                          display all usage information
                                                    types of info:
                                                        usage - only display the usage information and not options
                                                        json - display the format of the json file
Required Options 2:
    -F FILE --file FILE                             Options will come from a json file.  "--help json" for format of json file
                                        
Required Options 3:
    -j <int> --number-of-jobs <INT>                 total number of jobs in this workload
    
    --nodes <INT>                      total number of nodes in this cluster for this workload

    --number-of-resources <INT:fixed>               This dictates the number of resources used for each job and the kind of randomness.
                          <INT:INT:unif>            INT must be > 0
                          <FLOAT:FLOAT:norm>
                          <STR:pos:csv>      
                                                    fixed: All jobs will have INT for number of resources.
                                                    csv: Will come from file at STR.  pos is the position in each row that holds resources. 0 is first column.
                                                    unif: This will be uniform, random values from min:max
                                                    variations of min:max include:
                                                            :		    1 to the total amount of resources
                                                            min:		min to the total amount of resources
                                                            :max		1 to max
                                                            min:max		min to max
                                                    ex:     
                                                            '--number-of-resources "50:fixed"'
                                                            '--number-of-resources "::unif"'
                                                            '--number-of-resources "2::unif"'
                                                            '--number-of-resources ":10:unif"'
                                                            '--number-of-resources "2:10:unif"'
                                                            '--number-of-resources "~/500000.csv:0:csv"'

    
    --duration-time <FLOAT><:exp|fixed>             This dictates the duration times and what kind of randomness. FLOAT must be > 0.
                    <FLOAT:FLOAT:unif>
                    <FLOAT:FLOAT:norm>      
                    <STR:pos:time:csv>              exp: This will be exponentially distributed, random values with mean time of durations to be FLOAT.
                                                    fixed: All jobs will have FLOAT for a duration.
                                                    csv: Will come from file at STR.  pos is the position in each row that holds resources. 0 is first column. h|m|s for time.hour|minute|second
                                                    unif: This will be uniform, random values from min:max
                                                    ex:     
                                                            '--duration-time "200.0:exp"'
                                                            '--duration-time "100.0:fixed"
                                                            '--duration-time "0:200.0:unif"'
                                                            '--duration-time "~/500000.csv:1:h:csv"'
                  
    --submission-time <FLOAT><:exp|fixed>           This dictates the time between submissions and what kind of randomness.
                      <FLOAT:FLOAT:unif>            If zero is used for a float,combined with ":fixed" then all jobs will start at time zero.
                      <FLOAT:FLOAT:norm>
                                                            
                                                    exp: This will be exponentially distributed, random values with mean time between submissions to be FLOAT.
                                                    fixed: All jobs will have this time between them unless zero is used for a FLOAT.
                                                    unif: This will be uniform, random values from min:max
                                                    ex:     
                                                            '--submission-time "200.0:exp"'
                                                            '--submission-time "100.0:fixed"'
                                                            '--submission-time "0.0:fixed"'
                                                            '--submission-time "0:200.0:unif"'
Optional Options:
    -o PATH/FILE --output=PATH/FILE                 where output lives
                                                    [default: <number-of-jobs>_<nodes>.json]
                                                    
    --scaleTimeWidth INT                            Scale the time based on number of nodes
                                                                                        
    --wallclock-limit <FLOAT|INT%|STR>              wallclock limits will all be set to this for FLOAT. (-1) means the value will not be used in Batsim.
                                                    wallclock limits will be a % of run time for INT%
                                                    wallclock limits will be random from min % of runtime to max % in STR format '"min%:max%"'
                                                    wallclock limits will be random seconds from min to max in STR format  '"min:max"'
                                                    wallclock limits will be -1 if not set
                                                    ex:     '--wallclock-limit -1'
                                                            '--wallclock-limit 500.3'
                                                            '--wallclock-limit 101%'
                                                            '--wallclock-limit "50%:150%"'
                                                            '--wallclock-limit "100:3000"'

    --read-time <FLOAT|INT%|STR>                    set this fixed time to readtime in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random % of run time for STR format "min%:max%"
                                                    set this to random seconds from min to max in STR format   "min:max".
                                                    readtime will be omitted in the workload if not included.
                                                    ex:     '--read-time 20'
                                                            '--read-time 2%'
                                                            '--read-time "2%:4%"'
                                                            '--read-time "2:20"'

    --dump-time <FLOAT|INT%|STR>                    set this fixed time to dumptime in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random % of run time for STR format "min%:max%"
                                                    set this to random seconds from min to max in STR format   "min:max".
                                                    dumptime will be omitted in the workload if not included.
                                                    ex:     '--dump-time 20'
                                                            '--dump-time 3%'
                                                            '--dump-time "3%:5%"'
                                                            '--dump-time "3:30"'

    --checkpoint-interval <FLOAT|INT%|STR>          set this fixed time to checkpoint in seconds for FLOAT.
                                                    set this to % of run time for INT%.
                                                    set this to random % of run time for STR format "min%:max%"
                                                    set this to random seconds from min to max in STR format   "min:max".
                                                    checkpoint will be omitted in the workload if not included.
                                                    ex:     '--checkpoint-interval 120'
                                                            '--checkpoint-interval 30%'
                                                            '--checkpoint-interval "10%:30%"'
                                                            '--checkpoint-interval "120:240"'
  
"""


import pandas as pd
import numpy as np
import os
import json
import sys
from docopt import docopt,DocoptExit
import json

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False

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

def parseRandomChoiceString(aTimeStr,option,numberFunction,randomChoices,newSize):
    # if there is a colon (:)
    times=[]
    if not aTimeStr.find(":") == -1:
        STR = aTimeStr.split(":")
        #check if csv durations
        if len(STR) == 4:
            if not STR[3].find("csv")==-1 and "csv" in randomChoices:
                if os.path.exists(STR[0]):
                    df = pd.read_csv(STR[0],sep=",",header=None)
                    pos=int(STR[1])
                    time=STR[2]
                    df = df[:newSize]
                    times = df[df.columns[pos]].astype(numberFunction)
                    
                    if time == "h":
                        times=times * 3600
                    elif time == "m":
                        times=times * 60
                    elif time == "s":
                        times = times
                    else:
                        print("error on {option}: {time} is not a choice for time. \n{aTimeStr}".format(option=option,time=time,aTimeStr=aTimeStr))
                    times = list(times)
        
        elif len(STR) == 3:
            #check if uniform
            if not STR[2].find("unif")== -1 and "unif" in randomChoices:
                if numberFunction == int:
                    times = np.random.randint(low=numberFunction(STR[0]),high=numberFunction(STR[1]),size=newSize)
                else:
                    times = np.random.uniform(low=numberFunction(STR[0]),high=numberFunction(STR[1]),size=newSize)
            #check if normal
            if not STR[2].find("norm")==-1 and "norm" in randomChoices:
                if numberFunction == int:
                    times=np.round(np.random.normal(loc=float(STR[0]),scale=float(STR[1]),size=newSize))
                else:
                    times=np.random.normal(loc=float(STR[0]),scale=float(STR[1]),size=newSize)
            #check if csv resources
            elif not STR[2].find("csv")==-1 and "csv" in randomChoices:
                if os.path.exists(STR[0]):
                    df = pd.read_csv(STR[0],sep=",",header=None)
                    pos=int(STR[1])
                    #times = df.iloc[0:newSize,[pos]]
                    df = df[:newSize]
                    times = df[df.columns[pos]].astype(numberFunction)
                    times = list(times)
                    
                                      
        #check if fixed or exp
        elif len(STR)==2:
            if not STR[1].find("fixed")== -1 and "fixed" in randomChoices:
            
                time = numberFunction(STR[0])
                if time == 0 and option == "--submission-time":
                    times = [0] * newSize
                else:
                    times = [time] * newSize
            elif not STR[1].find("exp")== -1 and "exp" in randomChoices:
                if numberFunction == int:
                    times = np.round(np.random.exponential(float(STR[0]),newSize))
                else:
                    times = np.random.exponential(float(STR[0]),newSize)
    if len(times) == 0:
        print("you provided a String for " +option+ " in the wrong format")
        print(aTimeStr)
        sys.exit(1) 
    if option == "--submission-time":
        times[0] = 0
        times = np.cumsum(times)
    
    return times





try:
    args=docopt(__doc__,help=False,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

if args["<type-of-info>"] == "json":
    info="""
    JSON file will be in this format:

    {
        "total_jobs": ,                # total number of jobs in this workload
        "total_resources": ,           # total nodes in cluster this workload is running on
        "workload_A":{
                        "percent": ,   # where percent is an integer and all workloads add up to 100
                        "durations":{
                                        "X1_[h|m|s]":YY,   # where h,m,s is hrs,mins,or secs and YY is percent integer 
                                        "X2_[h|m|s]":YY    # where YY's add up to 100
                                        ...
                                    },
                        "job_sizes":{
                                        "X1":YY,    # where X1 is the cutoff of nodes and YY is percent integer
                                        "X2":YY     # where YY's add up to 100
                                        ...
                                    },
                        "submissions":INT,
                        "dump_time":INT,
                        "read_time":INT,
                        "[random-submissions|random-dump_time|random-read_time]":"min:max"
                    },
        "workload_B":{
                        ...
                    },
        ...
    }"""
    print(info)
    sys.exit(0)
elif args["<type-of-info>"] == "usage":
    info = """
       A program to generate a synthetic workload for Batsim Simulator

        Usage: 
            generate_synthetic_workload.py --help [<type-of-info>]
            generate_synthetic_workload.py -F FILE
            generate_synthetic_workload.py --number-of-jobs INT --nodes INT  --number-of-resources STR --duration-time STR --submission-time STR 
                                            [--output FILE]
                                            [--wallclock-limit <FLOAT|INT%|STR>]
                                            [--read-time <FLOAT|INT%|STR>] [--dump-time <FLOAT|INT%|STR>]
                                            [--checkpoint-interval <FLOAT|INT%|STR>]

        Arguments:
            FILE                                            an absolute location to a file
            PATH                                            an absolute location to a directory
            INT                                             an integer
            FLOAT                                           a decimal number
            STR                                             a string of characters


    """
    print(info)
    sys.exit(0)
elif args["--help"]:
    print(__doc__)
    sys.exit(0)
if args["--file"]:
    jsonFile = args["--file"]
    with open(jsonFile,"r") as InFile:
        jsonOptions = json.load(InFile)
    if dictHasKey(jsonOptions,"total_jobs"):
        total_jobs = int(jsonOptions["total_jobs"])
    if dictHasKey(jsonOptions,"total_resources"):
        total_resources = int(jsonOptions["total_resources"])
    workloads = list()
    for key in jsonOptions.keys():
        if not key.find("workload_") == -1:
            workloads.append(key)
    if len(workloads)==0:
        print("no workloads were detected in json file, refer to --json-info option for file format")
        sys.exit(1)
    total_percent = 0
    for workload in workloads:
        total_percent += jsonOptions[workload]["percent"]
    if total_percent != 100:
        print("workload percents do not add up to 100%, added up to:  " + str(total_percent))
        print("exiting")
        sys.exit(1)
    for workload in workloads:
        sys.exit(0)

#Required Options
#---------------------------------------

    #how many jobs?
number_of_jobs=int(args['--number-of-jobs'])

    #how many nodes in cluster?
totalResources = int(args['--nodes'])

    #number of resources?
numberResources = args['--number-of-resources']

    #durations ?
durationTime = args['--duration-time']

    #submission times?
submissionTime = args['--submission-time']

#Optional Options
#--------------------------------------

    #scale Times based on # nodes
oldNodes= int(args['--scaleTimeWidth']) if args['--scaleTimeWidth'] else False
    

    #location of output batsim workload
output_jobs="{jobs}_{res}.json".format(jobs=number_of_jobs, res=totalResources) if args['--output'] == "<number-of-jobs>_<workload-resources>.json" else args['--output']
    
    #wallclock limit
wallclockLimit = args['--wallclock-limit']
    
    #read time
readTime = args['--read-time']
    
    #dump time
dumpTime = args['--dump-time']
    
    #checkpoint interval
checkpointInterval = args['--checkpoint-interval']


#get ids of jobs
ids = list(range(1,number_of_jobs+1))
ids = [str(e) for e in ids ]

#get profile ids and types
types = ["delay"]*number_of_jobs
profileTypes=ids


#Handle Required Options
#--------------------------------------------------
if numberResources:
    resources = parseRandomChoiceString(numberResources,"--number-of-resources",int,["fixed","unif","norm","exp","csv"],number_of_jobs)
if durationTime:
    durations = parseRandomChoiceString(durationTime,"--duration-time",float,["fixed","unif","norm","exp","csv"],number_of_jobs)
if submissionTime:
    submissions = parseRandomChoiceString(submissionTime,"--submission-time",float,["fixed","unif","norm","exp"],number_of_jobs)
if oldNodes:
    resources_old=np.array(resources)
    durations_old=np.array(durations)
    cluster_old=oldNodes
    cluster_new=totalResources
    resources_new = np.round(resources_old*(cluster_new/cluster_old)).astype(int)
    durations_new = np.round((durations_old*resources_old)/resources_new).astype(int)
    durations=durations_new
    resources=resources_new
    
#set the required columns
cols=[ids,submissions,resources,ids]
column_names=["id","subtime","res","profile"]




#Handle Optional Options
#--------------------------------------------------
if wallclockLimit:
    wallclockLimits = parseTimeString(wallclockLimit,durations,number_of_jobs)
    cols.append(wallclockLimits)
    column_names.append("walltime")
if readTime:
    readTimes = parseTimeString(readTime,durations,number_of_jobs)
    cols.append(readTimes)
    column_names.append("readtime")
if dumpTime:
    dumpTimes = parseTimeString(dumpTime,durations,number_of_jobs)
    cols.append(dumpTimes)
    column_names.append("dumptime")
if checkpointInterval:
    checkpointIntervals = parseTimeString(checkpointInterval,durations,number_of_jobs)
    cols.append(checkpointIntervals)
    column_names.append("checkpoint")


#Create the json file
#----------------------------------------------------

    #first get all the columns of jobs into a list and then make a dataframe out of it
data=list(zip(*cols))
jobs=pd.DataFrame(data=data,columns=column_names)
    #scale Times if that is set


    #change the name of durations to make more sense of the json file
delay=durations
real_delay=delay

    #now get all the columns of profiles into a list and then make a dataframe out of it. notice the index
    #of the dataframe will have the profileTypes as its index.  Read why below.
data=list(zip(types,delay,real_delay))
profiles=pd.DataFrame(data=data,columns=["type","delay","real_delay"],index=profileTypes)

    #convert the dataframes to dictionaries,notice "orient" is "index" for profiles and "records" for jobs
    #This is because profiles are a list of dict of dicts whereas jobs are just a series of dicts
    #ie profiles 
    #       {"job_id_number1":{"type":"delay","delay":200,"real_delay":200},"job_id_number2":{...}}
    #vs jobs
    #       [{"option":value,"option":value,...},{"option":value,"option":value,...}]
profiles2dict=profiles.to_dict(orient="index")
jobs2dict=jobs.to_dict(orient="records")

    #add the data and the headings to our json
jsonData={"nb_res":totalResources,"jobs":jobs2dict,"profiles":profiles2dict}

    #now dump the jsonData into a file with nice formatting (indent=4)
with open(output_jobs, 'w') as outfile:
    json.dump(jsonData, outfile,indent=4)
