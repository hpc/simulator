"""
Usage:
    edit_workload.py --input <STR> [--output <STR>] [--copy-factor <INT>]
    edit_workload.py --help

Required Options 1:
    -i --input <STR>             The input workload in json format to apply multiply techniques to.

Optional Options 1:
    -o --output <STR>            The output workload in json format to output the changes to.
                                 default is to overwrite input.
                                 [default: --input]
    
    -c --copy-factor <INT>       The amount of copies ending file with have.
                                 2 here means if there was one job, id=1,
                                 there will be 1 copy of it made with a new unused id.
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
def copyWorkload(ourInput,ourOutput,copyFactor):
    
    def copyComponents(jobs,profiles,startId):

        jobs2=[]
        profiles2=deepcopy(profiles)
        count=0
        for i in jobs:
            job = deepcopy(i)
            if (dictHasKey(job,"purpose") and (job["purpose"] != "reservation")) or not dictHasKey(job,"purpose"):
                job["id"]=str(startId+count)
                job["profile"]=str(startId+count)
                jobs2.append(job)
            count+=1
        count=0
        for i in profiles:
            profile = deepcopy(profiles[i])
            profiles2.pop(i)
            profiles2[str(startId + count)]=profile
            count+=1
        return jobs2,profiles2

    with open(ourInput, "r") as jsonFile:
        workload = json.load(jsonFile)
    
    jobs = workload["jobs"]
    profiles=workload["profiles"]
    jobs_copy=deepcopy(jobs)
    profiles_copy=deepcopy(profiles)
    startId = int(jobs[len(jobs)-1]["id"]) + 1
    
    for i in range(0,copyFactor-1,1):
        jobs_returned,profiles_returned = copyComponents(jobs_copy,profiles_copy,startId)
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