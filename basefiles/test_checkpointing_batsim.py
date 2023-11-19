#!/usr/bin/env python3
"""
Usage: 
    test-checkpointing-batsim.py -i <path> -o <folder> [--prefix <path>] [--socket-start <INT>] 
                                                       [--task-start <int>] [--task-end <int>] [--start-counter <int>] [--end-counter <int>]
                                                       [--tasks-per-node <int>] [--method <STR>] [--parallel-method <STR>] [--wallclock-limit <STR>]
       
Required Options:
    -i , --input <path>            where the config file is
    --socket-start <INT>           where to start the socket count                     
                                   [default: 20000]
    -o , --output <folder>         where to put the output.  Will be put in
                                   $prefix/experiments/<folder>
    --prefix <path>                select a different prefix for output
                                   '--prefix/--output'
                                   [default: None]
    --task-start <int>             the task to start on
                                   [default: 1]
    --task-end <int>               the task to end on. -1 is all of the tasks
                                   [default: -1]
    --start-counter <int>          the startCounter to start at
                                   [default: 1]
    --end-counter <int>            the highest startCounter to do. -1 is all.
                                   [default: -1]
    -t, --tasks-per-node <int>     Amount of tasks per node
                                   [default: 1]
    -m, --method <STR>             What method to run batsim:
                                   'bare-metal' | 'docker' | 'charliecloud'
                                   [default: 'charliecloud']
    -p, --parallel-method <STR>    What method to spawn multiple batsims:
                                   'sbatch' | 'tasks' | 'none' | 'background'
                                   sbatch: individual sbatch commands for each sim
                                   tasks: --tasks-per-node sims per sbatch command, with enough sbatch's to complete config file generated sims
                                   none: no parallelism,only serial. Will run one sim after another (may take a VERY long time)
                                   background: will try to achieve parallelism by backgrounding each sim, backgrounding (--tasks-per-node - 1) sims before waiting
                                   [default: 'tasks']
    -w, --wallclock-limit <STR>    the wallclock-limit in SLURM format          
                                   [default: 12:00:00]
"""





import pandas as pd
import numpy as np
import json
from docopt import docopt
import sys
import os
import datetime as dt
import re
import functions
import coordinator
SECS=1
MINS=60*SECS
HOURS=60*MINS
DAYS=24*HOURS
MAX_SOCKETS_PER_CONFIG = 1000
PREFIX=os.getenv("prefix")
ourFolders={}
highestStart=1
InConfig = {}
def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def task_1():
    def run_base(file1,start,type,keep,socketStart,count):
        global ourFolders
        folder1 = f"{outputFolder}/{os.path.splitext(file1)[0]}_test_chkpt_base_{start}"
        folders=ourFolders[file1] if dictHasKey(ourFolders,file1) else []
        folders = folders + [folder1]
        ourFolders[file1]=folders
        with open(f"{PREFIX}/configs/{file1}","r") as InFile:
            config = json.load(InFile)
        for exp in config:
            myInput=config[exp]["input"]
            #we need to insert the two keys before workload
            #first lets pop them if they already exist
            myInput.pop("checkpoint-batsim-interval",None)
            myInput.pop("checkpoint-batsim-keep",None)
            #ok they are popped now lets insert at the right place
            #do we have a grizzly workload or a synthetic?
            if dictHasKey(myInput,"grizzly-workload"):
                pos = list(myInput.keys()).index('grizzly-workload')
            elif dictHasKey(myInput,"synthetic-workload"):
                pos = list(myInput.keys()).index('synthetic-workload')
            items = list(myInput.items())
            items.insert(pos, ("checkpoint-batsim-interval",f"{type}:{start}"))
            items.insert(pos+1,("checkpoint-batsim-keep",keep))
            myInput = dict(items)
            config[exp]["input"]=myInput
        with open(f"{PREFIX}/configs/{file1}",'w') as OutFile:
            json.dump(config,OutFile,indent=4)
        mainCmd=f"myBatchTasks.sh -f {file1} -o {folder1} -m charliecloud -t {tasksPN} -m {method} -p {pMethod} -s {socketStart} -w {wallClock}"
        command = f"source {PREFIX}/basefiles/batsim_environment.sh && {mainCmd}"
        os.system(command)
        return folder1
    
    #first move experiment.sh to experiment.sh.BAK
    #os.system(f"mv {PREFIX}/basefiles/experiment.sh {PREFIX}/basefiles/experiment.sh.BAK")
    #now change our alternate.sh to experiment.sh
    #os.system(f"mv {PREFIX}/basefiles/alternate.sh {PREFIX}/basefiles/experiment.sh")
    with open(configPath,"r") as InFile:
        global InConfig
        InConfig = json.load(InFile)

    configs=InConfig["configs"]
    #first run the checkpointing
    for config in configs:
        global highestStart
        global socketStart
        starts = config["starts"]
        highestStart = max(highestStart,max(functions.getIntervalValues(starts)))
        file = config["file"]
        checkpoints = config["checkpoints"]
        start = checkpoints["start"]
        keep = int(checkpoints["keep"])
        stagger = checkpoints["stagger"]
        count = checkpoints["count"]
        regEx=re.compile("^(?:(real|simulated):(\d+)-)?(\d+):(\d+):(\d+)")
        regMatch=regEx.match(start)
        type = regMatch[1]
        parts = [int(regMatch[i]) for i in [2,3,4,5]]
        seconds = (parts[0] * DAYS) + (parts[1] * HOURS) + (parts[2] * MINS) + (parts[3] * SECS)
        regMatch=regEx.match(stagger)
        #don't stagger in units greater than hours
        secondsToAdd = (parts[1] * HOURS ) + (parts[2] * MINS) + (parts[3] * SECS)
        for i in range(0,count,1):
            run_base(file,start,type,keep,socketStart,i)
            seconds+=secondsToAdd
            duration = dt.datetime.utcfromtimestamp(seconds)
            timeString = duration.strftime("%H:%M:%S")
            #%e will give wrong number, so figure out days by ourselves
            start=f"{int(seconds/DAYS)}-{timeString}"
            socketStart+=MAX_SOCKETS_PER_CONFIG
    #ok we started everything for the base
    #count how many Run_* folders there are for # of sims
    command = "find -type d -name \"Run_*\" | wc -l"
    nb_sims = os.popen(command).read()
    nb_sims = int(nb_sims)
    return nb_sims
def task_2():
    global startCounter
    global InConfig
    nb_sims=0
    configs = InConfig["configs"]
    #next run the start-from-checkpoints and evaluate
    #first let's clear the progress.log
    command = f"rm {outputFolder}/progress.log"
    os.system(command)
    for config in configs:
        #check if this config includes this start-from-checkpoint
        starts = functions.getIntervalValues(config["starts"])
        file1 = config["file"]
        if startCounter in starts:
            #it is, lets run it
            for folder1 in ourFolders[file1]:
                mainCmd=f"myBatchTasks.sh -f {file1} -o {folder1} -m charliecloud -t {tasksPN} -m {method} -p {pMethod} -s {socketStart} -w {wallClock} -D -S {startCounter}"
                command = f"source {PREFIX}/basefiles/batsim_environment.sh && {mainCmd}"
                os.system(command)
                command = f"find {folder1} -type d \"Run_*\" | wc -l"
                nb_sims += int(os.popen(command).read())
    return nb_sims
def task_3():
    #compare 
    global startCounter
    global InConfig
    configs = InConfig["configs"]
    for config in configs:
        #check if this config includes this start-from-checkpoint
        starts = functions.getIntervalValues(config["starts"])
        whatToCompare = config["compare"]
        file1 = config["file"]
        if startCounter in starts:
            with open(f"{outputFolder}/failedComparisons.log","a+") as OutFile:
                OutFile.write(f"{startCounter}:\n")
            #this config includes the start, lets compare files in these folders
            for folder1 in ourFolders[file1]:
                base=folder1
                experiments=[i for i in os.listdir(base) if os.path.isdir(base+"/"+i) and i!="heatmaps"]
                for exp in experiments:
                    jobs = [i for i in os.listdir(base+"/"+exp+"/")]
                    for job in jobs:
                        ids = [i for i in os.listdir(base+"/"+exp+"/"+job) if os.path.isdir(base+"/"+exp+"/"+job+"/"+i)]
                        for theId in ids:
                            runs = [i for i in os.listdir(base+"/"+exp+"/"+job+"/"+theId) if os.path.isdir(base+"/"+exp+"/"+job + "/" + theId +"/"+ i)]
                            for run in runs:
                                if whatToCompare == "post_out_jobs.csv":
                                    input1 = f"{base}/{exp}/{job}/{theId}/{run}/output/expe-out/post_out_jobs.csv"
                                    input2 = f"{base}/{exp}/{job}/{theId}/{run}/output/expe-out_1/post_out_jobs.csv"
                                    compareRet = functions.comparePostOutJobs(input1,input2)
                                elif whatToCompare == "makespan.csv":
                                    input1 = f"{base}/{exp}/{job}/{theId}/{run}/output/expe-out/makespan.csv"
                                    input2 = f"{base}/{exp}/{job}/{theId}/{run}/output/expe-out_1/makespan.csv"
                                    compareRet = functions.compareMakespan(input1,input2)
                                if compareRet == False:
                                    with open(f"{outputFolder}/failedComparisons.log","a+") as OutFile:
                                        OutFile.write(f"{input1}\n{input2}")
                

args=docopt(__doc__,help=True,options_first=False)
OutConfig={}
InConfig = {}
configPath=f"{PREFIX}/configs/{args['--input']}"
outputFolder=args["--output"]
outputPrefix=args["--prefix"]
if outputPrefix == "None":
    outputFolder=f"{PREFIX}/experiments/{outputFolder}"
else:
    outputFolder=f"{outputPrefix}/{outputFolder}"
nb_taskStart = int(args["--task-start"])
nb_taskEnd = int(args["--task-end"])
os.makedirs(outputFolder,exist_ok=True)
socketStart=int(args["--socket-start"])
startCounter = int(args["--start-counter"])
endCounter = int(args["--end-counter"])
wallClock=args["--wallclock-limit"]
method=args["--method"]
pMethod=args["--parallel-method"]
tasksPN=args["--tasks-per-node"]



if nb_taskStart == 1: 
    nb_sims = task_1()
    if nb_sims > 0:
        taskRet = coordinator.testCheckpointing(outputFolder,nb_sims)
    if taskRet == False:
        print("Error with task_1")
        sys.exit()
    if (nb_taskEnd > nb_taskStart) or (nb_taskEnd == -1):
        nb_taskStart+=1
if nb_taskStart == 2:
    if endCounter != -1:
        highestStart = endCounter
    for i in range(startCounter,highestStart+1,1):
        startCounter = int(i)
        nb_sims = task_2()
        if nb_sims > 0:
            taskRet = coordinator.testCheckpointing(outputFolder,nb_sims)
            if taskRet:
                task_3()
            else:
                print(f"Error with task_2   startCounter={startCounter}")
                sys.exit()


    

                
    