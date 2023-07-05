"""
    aggregate_batches.py    a helpful script to combine experiments that were done in batches
                            combines the runs of folderSRC with the runs in folderDST and outputs to folderDST
                            *NOTE*: folderSRC and folderDST should have the same amount of jobs (experiment_# folders)

Usage:
    aggregate_batches.py --folderSRC <STR> --folderDST <STR> (--runs <INT>|--ids <INT>) 

Required Options:
    --folderSRC <STR>    Where to look for extra runs.Absolute Path with slashes or in experiments folder

    --folderDST <STR>    Where to aggregate to. Absolute Path with slashes or in experiments folder
                         
    --runs <INT>         aggregation will be of runs, what number should folderSRC runs start at?

    --ids <INT>          aggregation will be of ids, what number should folderSRC ids start at?                  
    
"""


import pandas as pd
import numpy as np
from docopt import docopt,DocoptExit
import os
import re
import sys

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

scriptPath=str(os.path.dirname(os.path.abspath(__file__)))
folderSRC=str(args["--folderSRC"]) if str(args["--folderSRC"]).find("/")!=-1 else str(os.path.dirname(scriptPath))+"/experiments/"+str(args["--folderSRC"])
folderDST=str(args["--folderDST"]) if str(args["--folderDST"]).find("/")!=-1 else str(os.path.dirname(scriptPath))+"/experiments/"+str(args["--folderDST"])
folderSRC=folderSRC.rstrip("/")
folderDST=folderDST.rstrip("/")
aggregate="runs" if args["--runs"] else "ids"
numberStart = 0
if aggregate == "runs":
     numberStart = int(args["--runs"])
else:
     numberStart = int(args["--ids"])
experiments=[i for i in os.listdir(folderSRC) if os.path.isdir(os.path.join(folderSRC,i)) and (i!="total_waiting_time") and (i!="total_waiting_time_maxs") and (i!="pp_slowdown")]
for exp in experiments:
            jobs = [i for i in os.listdir(os.path.join(folderSRC,exp)) if os.path.isdir(os.path.join(folderSRC,exp,i))]
            jobs.sort(key=natural_keys)
            for job in jobs:
                ids1 = [i for i in os.listdir(os.path.join(folderSRC,exp,job)) if os.path.isdir(os.path.join(folderSRC,exp,job,i))]
                ids1.sort(key=natural_keys)
                #ids2 = [int(i.lstrip("id_")) for i in os.listdir(os.path.join(folderDST,exp,job)) if os.path.isdir(os.path.join(folderDST,exp,job,i))]
                startId= numberStart
                for id in ids1:
                    if aggregate == "ids":
                        newId=f"id_{startId}"
                        command = f"cp -R {os.path.join(folderSRC,exp,job,id)} {os.path.join(folderDST,exp,job,newId)}"
                        os.system(command)
                        newId+=1
                    else:
                        runs1 = [i for i in os.listdir(os.path.join(folderSRC,exp,job,id)) if os.path.isdir(os.path.join(folderSRC,exp,job,id,i))]
                        runs1.sort(key=natural_keys)
                        #runs2 = [int(i.lstrip("Run_")) for i in os.listdir(os.path.join(folderDST,exp,job,id)) if os.path.isdir(os.path.join(folderDST,exp,job,id,i))]
                        startRun = numberStart
                        
                        for run in runs1:
                            newRun=f"Run_{startRun}"
                            command = f"cp -R {os.path.join(folderSRC,exp,job,id,run)} {os.path.join(folderDST,exp,job,id,newRun)}"
                            os.system(command)
                            startRun+=1
                    
                    
