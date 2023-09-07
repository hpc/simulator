"""
A program to generate a synthetic workload for Batsim Simulator

Usage: 
    generate_synthetic_workload.py --help [<type-of-info>]
    generate_synthetic_workload.py -F FILE
    generate_synthetic_workload.py --db FILE --file-name FILE
    generate_synthetic_workload.py --number-of-jobs INT --nodes INT  --number-of-resources STR --duration-time STR --submission-time STR --type STR [--machine-speed FLOAT]
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
                                                        usage-full - displays full usage info, also displayed when type of info is blank
                                                        usage - only display the usage information and not options
                                                        json - display the format of the json file
Required Options 2:
    -F, --file FILE                                 Options will come from a json file.  "--help json" for format of json file
Required Options 3:
    --db FILE                                       path to database csv file to add workload(s) to                                    
    --file-name FILE                                output file name that also serves as the look-up name in the database for all the options

Required Options 4:
    -j <int> --number-of-jobs <INT>                 total number of jobs in this workload
    
    --nodes <INT>                                   total number of nodes in this cluster for this workload

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
    --type <STR>                                    Type of profile: delay || parallel_homogeneous
    
    --machine-speed <FLOAT>                         The speed (in flops/s) of the machines this will run on, used for type: parallel_homogeneous
    
Optional Options:
    -o PATH/FILE --output=PATH/FILE                 where output lives
                                                    [default: <number-of-jobs>_<nodes>.json]
                                                                                        
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

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False

def parseTimeString(aTimeStr,durations_times,newSize):
    times=[]
    # if it is an integer or float
    if isinstance(aTimeStr,int) or isinstance(aTimeStr,float):
        time = float(aTimeStr)
        times = [time] * newSize
    else:
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
            percent = 0
            if not aTimeStr.find(".") == -1:
                percent = float(aTimeStr.rstrip("%"))
            else:
                percent = int(aTimeStr.rstrip("%"))
            for time in durations_times:
                times.append(np.ceil(time*(percent/100)))
    
    return times

def parseRandomChoiceString(aTimeStr,option,numberFunction,randomChoices,newSize,seed):
    # if there is a colon (:)
    import os
    times=[]
    if seed:
        np.random.seed(seed)
    else:
        np.random.seed()
    if not aTimeStr.find(":") == -1:
        STR = aTimeStr.split(":")
        #check if csv durations
        if len(STR) == 4:
            if not STR[3].find("csv")==-1 and "csv" in randomChoices:
                aFile=STR[0]
                print(aFile)
                if not os.path.exists(aFile):
                    #ok the path does not exist
                    #try using the script path
                    basename=str(os.path.basename(aFile))
                    aFile=str(os.path.dirname(os.path.abspath(__file__)))+"/"+basename
                    print(aFile)
                if os.path.exists(aFile):
                    df = pd.read_csv(aFile,sep=",",header=None)
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
                    #check if we need to add STR[1]
                    if STR[1] == '':
                        STR[1] = newSize
                    #check if we need to add STR[0]
                    if STR[0] == '':
                        STR[0] = 1
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
                aFile=STR[0]
                print(aFile)
                if not os.path.exists(aFile):
                    #ok the path does not exist
                    #try using the script path
                    basename=str(os.path.basename(aFile))
                    aFile=str(os.path.dirname(os.path.abspath(__file__)))+"/"+basename
                    print(aFile)
                if os.path.exists(aFile):
                    df = pd.read_csv(aFile,sep=",",header=None)
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

def generate_reservations_from_json(reservations_json):
    import reservations as rsv
    reservations = rsv.generate_reservations(reservations_json)
    return reservations

def generate_workload_from_json(workload_json):
    # every json has these
    speed=workload_json["machine-speed"] if dictHasKey(workload_json,"machine-speed") else -1
    totalResources = int(workload_json["total-resources"])
    numberOfJobs =int(workload_json["number-of-jobs"])
    workload=()
    # do we have a "workload-types" key?
    if dictHasKey(workload_json,"workload-types"):
        for workload_type in workload_json["workload-types"]:
            profileType = workload_type["type"]
            numberResources = workload_type["number-of-resources"]
            durationTime = workload_type["duration-time"]
            submissionTime = workload_type["submission-time"]
            percent = workload_type["percent"]
            wallclockLimit = workload_type["wallclock-limit"] if dictHasKey(workload_type,"wallclock-limit") else False
            dumpTime = workload_type["dump-time"] if dictHasKey(workload_type,"dump-time") else False
            readTime = workload_type["read-time"] if dictHasKey(workload_type,"read-time") else False
            checkpointInterval = workload_type["checkpoint-interval"] if dictHasKey(workload_type,"checkpoint-interval") else False
            workload=generate_workload(speed=speed,profile_type=profileType,number_of_jobs=numberOfJobs,total_resources=totalResources,\
                              number_resources=numberResources,duration_time=durationTime,submission_time=submissionTime,\
                               percent=percent,\
                               wallclock_limit=wallclockLimit,read_time=readTime,dump_time=dumpTime,checkpoint_interval=checkpointInterval,\
                               add_to_workload=workload)
    else:
        profileType = workload_json["type"]
        numberResources = workload_json["number-of-resources"]
        durationTime = workload_json["duration-time"]
        submissionTime = workload_json["submission-time"]
        seed = workload_json["seed"] if dictHasKey(workload_json,"seed") and (workload_json["seed"]!="False") else False
        wallclockLimit = workload_json["wallclock-limit"] if dictHasKey(workload_json,"wallclock-limit") else False
        dumpTime = workload_json["dump-time"] if dictHasKey(workload_json,"dump-time") else False
        readTime = workload_json["read-time"] if dictHasKey(workload_json,"read-time") else False
        checkpointInterval = workload_json["checkpoint-interval"] if dictHasKey(workload_json,"checkpoint-interval") else False
        if seed:
            print(f"seed:{seed}")
            np.random.seed(int(seed))
        else:
            print(f"no seed")
            np.random.seed()
        workload=generate_workload(speed=speed,profile_type=profileType,number_of_jobs=numberOfJobs,total_resources=totalResources,\
                            number_resources=numberResources,duration_time=durationTime,submission_time=submissionTime,\
                            wallclock_limit=wallclockLimit,read_time=readTime,dump_time=dumpTime,checkpoint_interval=checkpointInterval)
    return (totalResources,workload[1],workload[2])
    

def generate_workload(*,speed,profile_type,number_of_jobs,total_resources,number_resources,\
                    duration_time,submission_time,percent=100,wallclock_limit=None,read_time=None,dump_time=None,\
                    checkpoint_interval=None,add_to_workload=None,seed=False):
    startIds=1
    previousJobs=pd.DataFrame()
    previousProfiles=pd.DataFrame()
    if not add_to_workload == None:
        startIds =len(add_to_workload[0])
        previousJobsDict=add_to_workload[0]
        previousProfilesDict=add_to_workload[1]
        previousJobs=pd.DataFrame.from_dict(data=previousJobsDict)
        previousProfiles=pd.DataFrame.from_dict(data=previousProfilesDict,orient='index')
    #get ids of jobs
    number_of_jobs = int(number_of_jobs*(percent/100))

    ids = list(range(startIds,number_of_jobs+1))
    ids = [str(e) for e in ids ]

    #get profile ids and types
    if profile_type == "delay":
        types = ["delay"]*number_of_jobs
    else:
        types = ["parallel_homogeneous"] * number_of_jobs
    profileTypes=ids


    #Handle Required Options
    #--------------------------------------------------
    if number_resources:
        resources = parseRandomChoiceString(number_resources,"--number-of-resources",int,["fixed","unif","norm","exp","csv"],number_of_jobs,seed)
    if duration_time:
        durations = parseRandomChoiceString(duration_time,"--duration-time",float,["fixed","unif","norm","exp","csv"],number_of_jobs,seed)
    if submission_time:
        submissions = parseRandomChoiceString(submission_time,"--submission-time",float,["fixed","unif","norm","exp"],number_of_jobs,seed)

    #set the required columns
    cols=[ids,submissions,resources,ids]
    column_names=["id","subtime","res","profile"]




    #Handle Optional Options
    #--------------------------------------------------
    if wallclock_limit:
        wallclockLimits = parseTimeString(wallclock_limit,durations,number_of_jobs)
        cols.append(wallclockLimits)
        column_names.append("walltime")
    if read_time:
        readTimes = parseTimeString(read_time,durations,number_of_jobs)
        cols.append(readTimes)
        column_names.append("readtime")
    if dump_time:
        dumpTimes = parseTimeString(dump_time,durations,number_of_jobs)
        cols.append(dumpTimes)
        column_names.append("dumptime")
    if checkpoint_interval:
        checkpointIntervals = parseTimeString(checkpoint_interval,durations,number_of_jobs)
        cols.append(checkpointIntervals)
        column_names.append("checkpoint_interval")


    #Create the json file
    #----------------------------------------------------

        #first get all the columns of jobs into a list and then make a dataframe out of it
    data=list(zip(*cols))
    jobs=pd.DataFrame(data=data,columns=column_names)

        #change the name of durations to make more sense of the json file
    delay=durations
    real_delay=delay
    if profile_type == "delay":
            #now get all the columns of profiles into a list and then make a dataframe out of it. notice the index
            #of the dataframe will have the profileTypes as its index.  Read why below.
        data=list(zip(types,delay,real_delay))

        profiles=pd.DataFrame(data=data,columns=["type","delay","real_delay"],index=profileTypes)
    else:
            #convert times to cpu
        delay = [duration * speed for duration in durations]
        real_delay = delay
        com = [0] * number_of_jobs
        
        data=list(zip(types,delay,com,real_delay))
        profiles=pd.DataFrame(data=data,columns=["type","cpu","com","real_cpu"],index=profileTypes)   

    if not add_to_workload == None:
        jobs=pd.concat([previousJobs,jobs])
        jobs["id"]=jobs["id"].astype('int')
        jobs.sort_values(by="id")
        jobs["id"]=jobs["id"].astype('str')

        profiles=pd.concat([previousProfiles,profiles])



        
        
        

        #convert the dataframes to dictionaries,notice "orient" is "index" for profiles and "records" for jobs
        #This is because profiles are a list of dict of dicts whereas jobs are just a series of dicts
        #ie profiles 
        #       {"job_id_number1":{"type":"delay","delay":200,"real_delay":200},"job_id_number2":{...}}
        #vs jobs
        #       [{"option":value,"option":value,...},{"option":value,"option":value,...}]
    profiles2dict=profiles.to_dict(orient="index")
    jobs2dict=jobs.to_dict(orient="records")
    return (total_resources,jobs2dict,profiles2dict)

def add_reservations_to_workload(aWorkload,reservations):
    wJobs2dict=aWorkload[1]
    wProfiles2dict=aWorkload[2]
    endId = int(wJobs2dict[len(wJobs2dict)-1]["id"])
    jobs2dict=reservations[0]
    profiles2dict=reservations[1]
    
    count=endId+1
    #change the reservations jobs ids and profile names
    for i in range(0,len(jobs2dict),1):
        jobDict=jobs2dict[i]
        jobDict["id"]=str(count)
        jobDict["profile"]=str(count)
        jobs2dict[i]=jobDict
        count+=1
    #change the profiles keys
    
    #first get the keys and sort them
    myList=list(profiles2dict.keys())
    myList=[int(i) for i in myList]
    myList.sort()
    #get the start and end ids of reservations
    proStartId=myList[0]
    proEndId=myList[len(myList)-1]

    
    #now start at the ending id of the workload jobs +1
    #and set a dict with that key equal to the corresponding reservation profile dict
    count=endId+1
    profiles2dict_new={}
    for i in range(proStartId,proEndId+1,1):
        #remove the dict from profiles2dict and keep the returned dict
        proDict=profiles2dict.pop(str(i))
        profiles2dict_new[str(count)]=proDict
        
        count+=1
    
    # now jobs2dict and profiles2dict has been updated for the reservations
    # we just need to add them to the jobs2dict and profiles2dict of the workload
    wJobs2dict.extend(jobs2dict)
    wProfiles2dict.update(profiles2dict_new)
    return (aWorkload[0],wJobs2dict,wProfiles2dict)




try:
    args=docopt(__doc__,help=False,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

if args["<type-of-info>"] == "json":
    info="""
    JSON file will be in this format:

    {
        "reservations-name1":{
            "reservation-array":[
                {
                    "type":"parallel_homogeneous",
                    "machines":{
                        "prefix":"a",
                        "machine-speed":1,
                        "total-resources":"0-1489",
                        "interval":"0-744"                        
                    },
                    "repeat-every":"5months 5days 05:05:05",    
                    "time": "5months 5days 05:05:05",          
                    "start":"5months 5days 05:05:05",           
                    "submit-before-start":"5months 5days 05:05:05",
                    "count":200
                },
                   {
                    "type":"delay",
                    "machines":{
                        "prefix":"a",
                        "resources":5                        
                    },
                    "repeat-every":"5months 5days 05:05:05",    
                    "time": "5months 5days 05:05:05",          
                    "start":"5months 5days 05:05:05",           
                    "submit":-1,
                    "count":200
                }
            ],
            "options":{
                "no-collisions":"True"
            }
        },

        "synthetic-workloads":[
                                {
                                    "file-name":"~/basefiles/workloads/wl1.json",
                                    "number-of-jobs":3000,
                                    "total-resources":1490,
                                    "reservations":"name1",

                                    "type":"parallel-homogeneous",
                                    "machine-speed":1,
                                    "number-of-resources":"/ac-project/cwalker/basefiles/wl4.csv:0:csv", 
                                    "duration-time":"/ac-project/cwalker/basefiles/wl4.csv:1:h:csv", 
                                    "submission-time":"0:fixed", 
                                    "wallclock-limit":-1, "dump-time":"3%", 
                                    "read-time":"2%"
                                },

                                {
                                    "file-name":"~/basefiles/workloads/wl2.json",
                                    "number-of-jobs":8000,
                                    "total-resources":1490,
                                    
                                    "type":"parallel-homogeneous",
                                    "machine-speed":1,
                                    "number-of-resources":"/ac-project/cwalker/basefiles/wl2.csv:0:csv", 
                                    "duration-time":"/ac-project/cwalker/basefiles/wl2.csv:1:h:csv", 
                                    "submission-time":"0:fixed", 
                                    "wallclock-limit":-1, "dump-time":"3%", 
                                    "read-time":"2%"
                                },
                                {
                                    "file-name":"~/basefiles/workloads/wl3.json",
                                    "number-of-jobs":8000,
                                    "total-resources":1490,
                                    "machine-speed":1,
                                    "workload-types":[
                                                        {
                                                            "percent":80,
                                                            "type":"parallel-homogeneous",
                                                            "number-of-resources":"/ac-project/cwalker/basefiles/wl2.csv:0:csv", 
                                                            "duration-time":"/ac-project/cwalker/basefiles/wl2.csv:1:h:csv", 
                                                            "submission-time":"0:fixed", 
                                                            "wallclock-limit":-1, "dump-time":"3%", 
                                                            "read-time":"2%"
                                                        },
                                                        {
                                                            "percent":20,
                                                            "type":"parallel-homogeneous",
                                                            "number-of-resources":"/ac-project/cwalker/basefiles/wl2.csv:0:csv", 
                                                            "duration-time":"/ac-project/cwalker/basefiles/wl2.csv:1:h:csv", 
                                                            "submission-time":"0:fixed", 
                                                            "wallclock-limit":-1, "dump-time":"6%", 
                                                            "read-time":"2%"
                                                        }
                                                    ]
                                },
                                
                            ]
        
    }"""
    print(info)
    sys.exit(0)
elif args["<type-of-info>"] == "usage":
    info = """
       A program to generate a synthetic workload for Batsim Simulator

        Usage: 
            generate_synthetic_workload.py --help [<type-of-info>]
            generate_synthetic_workload.py -F FILE
            generate_synthetic_workload.py --db FILE --file-name FILE
            generate_synthetic_workload.py --number-of-jobs INT --nodes INT  --number-of-resources STR --duration-time STR --submission-time STR 
                                            [--output FILE]
                                            [--wallclock-limit <FLOAT|INT%|STR>]
                                            [--read-time <FLOAT|INT%|STR>] [--dump-time <FLOAT|INT%|STR>]
                                            [--checkpoint-interval <FLOAT|INT%|STR>]

        Arguments:
            FILE                                            an absolute location to a file
            PATH                                            an absolute location to a directory
            INT                                             an integer
            INT%                                            a string made with an integer followed by a '%'.  This value represents a percent of duration.
            FLOAT                                           a decimal number
            STR                                             a string of characters


    """
    print(info)
    sys.exit(0)
elif args["<type-of-info>"] == "usage-full":
    print(__doc__)
    sys.exit(0)
elif args["--help"]:
    print(__doc__)
    sys.exit(0)
if args["--file"]:
    jsonFile = args["--file"]
    jsonConfig={}
    with open(jsonFile,"r") as InFile:
        jsonConfig = json.load(InFile)
    rString="reservations-"
    wString="synthetic-workloads"
    reservations={}
    workloads={}
    # first check on reservations
    for key in jsonConfig.keys():
        if not key.find(rString) == -1:
            #ok we found a reservations key
            #get the name of it
            name=key[len(rString):]
            #now make the reservations.  They will have ids to them
            #we have a function add_reservations_to_workload() to change the ids
            reservations[name]=generate_reservations_from_json(jsonConfig[key])
    #next check on workloads
    if dictHasKey(jsonConfig, "synthetic-workloads"):
        for workload in jsonConfig[wString]:


            file_name=workload["file-name"]
            aWorkload = generate_workload_from_json(workload)
            if dictHasKey(workload,"reservations"):
                reservations_name=workload["reservations"]
                workloads[file_name]=add_reservations_to_workload(aWorkload,reservations[reservations_name])
            else:
                workloads[file_name]=aWorkload
    elif dictHasKey(jsonConfig, "synthetic-workload"):
        workload=jsonConfig["synthetic-workload"]
        file_name=workload["file-name"]
        aWorkload = generate_workload_from_json(workload)
        if dictHasKey(workload,"reservations"):
            reservations_name=workload["reservations"]
            workloads[file_name]=add_reservations_to_workload(aWorkload,reservations[reservations_name])
        else:
            workloads[file_name]=aWorkload
    for file,workload in workloads.items():
            #add the data and the headings to our json
        jsonData={"nb_res":workload[0],"jobs":workload[1],"profiles":workload[2]}
    
            #now dump the jsonData into a file with nice formatting (indent=4)
        with open(file, 'w') as outfile:
            json.dump(jsonData, outfile,indent=4)
    sys.exit(0)
if args["--db"]:
    
    
    
    database=pd.read_csv(args["--db"],sep="|",header=0)
    filename=args["--file-name"]
    df=database.loc[database.filename == filename]
    #ok now df has all the info we need
    cols=["filename","nodes","number-of-jobs","index","type","machine-speed","number-of-resources","duration-time","submission-time","wallclock-limit","read-time","dump-time","checkpoint-interval","scale-widths-based-on","scale-time-width-based-on","reservation-json"]

    speed=int(df["machine-speed"].values[0])
    profile_type=df["type"].values[0]
    number_of_jobs=int(df["number-of-jobs"].values[0])
    totalResources=int(df["nodes"].values[0])
    numberResources=df["number-of-resources"].values[0]
    durationTime=df["duration-time"].values[0]
    submissionTime=df["submission-time"].values[0]
    wallclockLimit=df["wallclock-limit"].values[0]
    readTime=df["read-time"].values[0]
    dumpTime=df["dump-time"].values[0]
    checkpointInterval=df["checkpoint-interval"].values[0]
    reservation_json=df["reservation-json"].values[0]
    seed=int(df["seed"].values[0]) if df["seed"].values[0]!="False" else False

    reservations=False
    if not ((reservation_json == False) or (reservation_json == "False")):
        reservations=generate_reservations_from_json(reservation_json)
        
    workload=generate_workload(speed=speed,profile_type=profile_type,number_of_jobs=number_of_jobs,total_resources=totalResources,number_resources=numberResources,\
                        duration_time=durationTime,submission_time=submissionTime,wallclock_limit=wallclockLimit,read_time=readTime,dump_time=dumpTime,\
                        checkpoint_interval=checkpointInterval,seed=seed)
    if reservations:
        workload=add_reservations_to_workload(workload, reservations)
    jsonData={"nb_res":totalResources,"jobs":workload[1],"profiles":workload[2]}
    file=os.path.dirname(str(args["--db"]))+"/"+str(args["--file-name"])
    with open(file, 'w') as outfile:
        json.dump(jsonData, outfile,indent=4)
    sys.exit(0)
    

#Required Options
#---------------------------------------
speed = -1
    #what profile type?
profile_type = args['--type']
if profile_type == "parallel_homogeneous":
    speed = float(args['--machine-speed'])

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

workload=generate_workload(speed=speed,profile_type=profile_type,number_of_jobs=number_of_jobs,total_resources=totalResources,number_resources=numberResources,\
                    duration_time=durationTime,submission_time=submissionTime,wallclock_limit=wallclockLimit,read_time=readTime,dump_time=dumpTime,\
                    checkpoint_interval=checkpointInterval)


    #add the data and the headings to our json
jsonData={"nb_res":totalResources,"jobs":workload[0],"profiles":workload[1]}

    #now dump the jsonData into a file with nice formatting (indent=4)
with open(output_jobs, 'w') as outfile:
    json.dump(jsonData, outfile,indent=4)
