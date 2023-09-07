"""
Usage:
    edit_workload.py --input <STR> [--output <STR>] [--copy-factor <STR>]
    edit_workload.py --help

Required Options 1:
    -i --input <STR>             The input workload in json format to apply multiply techniques to.

Optional Options 1:
    -o --output <STR>            The output workload in json format to output the changes to.
                                 default is to overwrite input.
                                 [default: --input]
    
    -c --copy-factor <STR>       The amount of copies the ending file with have, along with other optional options
                                 format: '<#copies>[:(+|-) #:(fixed|#[:unif:(single|each-copy|all)[:<seed#>] ])'
                                 So you can just do number of copies, or
                                 you can add a submission time to add some jitter
                                 This submission time is either added or subtracted (+|-)
                                 This time can be a fixed number followed by :fixed or uniform random number between 2 numbers
                                 If random you need to specify the second number with :#:unif:
                                 If random you then need to specify:
                                 'single' random number
                                 single random number for 'each-copy'
                                 or all different random numbers
                                 2 here means if there was one job, id=1,
                                 there will be 1 copy of it made with a new unused id.
                                 ' Examples:
                                 '                       '2'    - 2 copies no jitter
                                 '            '2:+:10:fixed'    - 2 copies, add 10 seconds fixed jitter to submission times
                                 '            '2:-:10:fixed'    - 2 copies, subtract 10 seconds fixed jitter from submission times
                                 '    '2:+:5:10:unif:single'    - 2 copies, get random number between 5 and 10 and add it to all copied submission times
                                 '    '3:+:5:10:unif:all:20'    - 3 copies, get random numbers between 5 and 10 for all jobs of all copies, add it to submission times
                                 '                                  and seed the random generator with 20
                                 ' '3:+:5:10:unif:each-copy'    - 3 copies, get random number between 5 and 10 and add it to all submission times of first copy
                                 '                                  then get another random number between 5 and 10 and add it to all sub times of second copy
                                 [default: 2]

Required Options 2:
    -h  --help                   output this usage page
"""

from docopt import docopt,DocoptExit
import pandas as pd
import numpy as np
import os
import sys
import json
from copy import deepcopy

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def parseCopyFactor(copyFactor):
    import re
    #can be just an int or followed by +|- followed by :int followed by fixed|:int, if :int followed by :unif: followed by single|each-copy|all optionally followed by :int
    regEx = re.compile("([0-9]+)(?:$|(?:[:]([+]|[-]):([0-9]+):(fixed|[0-9]+)(?:$|(?:[:](unif):(single|each[-]copy|all)(?:$|(?:[:]([0-9]+)))))))")
    match = regEx.match(copyFactor)
    #match.groups() [0]=int [1]=+|-|None [2]=int|None [3]=fixed|int|None [4]=unif|None [5]=single|each-copy|all|None [6]=int|None
    if match:
        myGroups = match.groups()
        return {"copies":int(myGroups[0]),"addSub":myGroups[1],"num1":myGroups[2],"num2":myGroups[3],"unif":myGroups[4],"howMany":myGroups[5],"seed":myGroups[6]}
    else:
        print(f"Error with copy key.  Invalid value: {copyFactor} ")
def copyWorkload(ourInput,ourOutput,copyFactor):
    parsed=parseCopyFactor(copyFactor)
    copyFactor = int(parsed["copies"])
    if parsed["seed"]:
        #ok we need to seed the random generator
        np.random.seed(int(parsed["seed"]))
    else:
        np.random.seed()
    
    def copyComponents(jobs,profiles,startId,parsed,randomNumber):

        jobs2=[]
        profiles2=deepcopy(profiles)
        alter=[]
        # now we can get our altered submission times if that was part of our --copy-factor string
        if parsed["num1"]:
            #ok we have an alteration to do
            if parsed["num2"]=="fixed":
                #ok there was a number and it is fixed
                # alter submit by this number
                alter = [int(parsed["num1"])]*len(jobs)
            elif parsed["howMany"] == "single":
                # ok we need a single random number, have we gotten it yet?
                if not randomNumber:
                    randomNumber = np.random.randint(low=int(parsed["num1"]),high=int(parsed["num2"]),size=1)[0]
                alter = [randomNumber]*len(jobs)
            elif parsed["howMany"] == "each-copy":
                #ok we need a single random number each time
                randomNumber = np.random.randint(low=int(parsed["num1"]),high=int(parsed["num2"]),size=1)[0]
                alter = [randomNumber]*len(jobs)
            elif parsed["howMany"] == "all":
                #ok we need a new random number for each submission
                alter = np.random.randint(low=int(parsed["num1"]),high=int(parsed["num2"]),size=len(jobs))
        count=0
        for i in jobs:
            job = deepcopy(i)
            if (dictHasKey(job,"purpose") and (job["purpose"] != "reservation")) or not dictHasKey(job,"purpose"):
                #ok, job is not a reservation.  Lets copy it with a new job id and profile
                job["id"]=str(startId+count)
                job["profile"]=str(startId+count)
                #do we need to alter submission times?
                if len(alter)>0:
                    #we do
                    original_submission=float(job["subtime"])
                    
                    job["subtime"]=original_submission + alter[count]
                    
                jobs2.append(job)
            count+=1
        count=0
        for i in profiles:
            profile = deepcopy(profiles[i])
            profiles2.pop(i)
            profiles2[str(startId + count)]=profile
            count+=1
        return jobs2,profiles2,randomNumber

    with open(ourInput, "r") as jsonFile:
        workload = json.load(jsonFile)
    
    jobs = workload["jobs"]
    profiles=workload["profiles"]
    jobs_copy=deepcopy(jobs)
    profiles_copy=deepcopy(profiles)
    startId = int(max(jobs, key=lambda job: job['id'])['id'])+1
    randomNumber=None
    for i in range(0,copyFactor-1,1):
        jobs_returned,profiles_returned,randomNumber = copyComponents(jobs_copy,profiles_copy,startId,parsed,randomNumber)
        jobs.extend(jobs_returned)
        profiles.update(profiles_returned)
        startId = int(jobs[len(jobs)-1]["id"]) + 1
    workload["jobs"]=jobs
    workload["profiles"]=profiles
    with open(ourOutput,"w") as outFile:
        json.dump(workload,outFile,indent=4)
if __name__ == '__main__': 
    try:
        args=docopt(__doc__,help=True,options_first=False)
    except DocoptExit:
        print(__doc__)
        sys.exit(1)

    
    ourInput = str(os.path.abspath(args["--input"]))
    ourOutput = ourInput if args["--output"] == "--input" else str(os.path.abspath(args["--output"]))
    copyFactor= int(args["--copy-factor"])
    copyWorkload(ourInput,ourOutput,copyFactor)
