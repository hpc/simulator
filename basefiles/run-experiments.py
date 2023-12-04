"""
    run-experiments:                once a directory structure is made using generate_config.py, this will run the experiments
                                    prepared with the generate_config.py script.  This can be run in parallel and single mode.

Usage:
    run-experiments.py -i <FOLDER> [--parallel-mode STR][--method STR][--partition STR][--cores-per-job INT][--socket-start INT][--time INT][--sim-time-minutes FLOAT | --sim-time-seconds INT][--start-run INT][--end-run INT] [--highest-priority] [--add-to-sbatch STR]
    run-experiments.py -i <FOLDER> [--parallel-mode STR][--method STR][--partition STR][--tasks-per-node INT][--socket-start INT][--time INT][--sim-time-minutes FLOAT | --sim-time-seconds INT][--start-run INT][--end-run INT] [--highest-priority] [--add-to-sbatch STR]

Required Options:
    -i <FOLDER> --input <FOLDER>    Where experiments live

Optional Important Options:

   --parallel-mode STR              The mode of parallelism:
                                    'sbatch' | 'tasks' | 'none'
                                    [default: tasks]

   --method STR                     Which method batsim is being run:
                                    'bare-metal','charliecloud','docker'
                                    [default: bare-metal]

   --partition STR                  The partition on slurm that you are submitting to.
                                    If not set, will get this information from SBATCH_PARTITION
                                    environment variable.
                                    [default: False]

   --cores-per-job INT              How many nodes to use per job.  Helps with spacing out
                                    large experiments that use a lot of memory.  Only used with
                                    '--parallel-mode sbatch'
                                    [default: 1]

   --tasks-per-node INT             How many tasks to use per job.  Helps with spacing out
                                    large experiments, as well as being necessary for systems
                                    where sbatch allocates exclusive access to its nodes.  This
                                    option will initiate an sbatch with srun commands. Only used with
                                    '--parallel-mode tasks' and mandatory when using that mode.
                                    [default: False]

   --socket-start INT               What socket number to start at. You must do your own housekeeping of sockets.  If you already
                                    have 100 sims going and you started at 10,000, then you will want to do your next set of sims at 10,100 for example
                                    You can use higher numbers.  I've used numbers up to 300,000
                                    [default: 10000]
Not So Important Options:
   --add-to-sbatch STR              If parallel-mode is not 'none' then one can add sbatch options.  These should
                                    overrule any environment variables set.

   --time STR                       The wallclock limit of each submitted simulation
                                    The unit is hours by default.  The default is actually to let
                                    SLURM decide, ie it doesn't specify a time by default.  This explicitly sets it.
                                    STR is in format:
                                    "minutes", "minutes:seconds", "hours:minutes:seconds", 
                                    "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
                                    ex: '48' , '48:30', '2:48:30'   48 minutes, 48.5 minutes, 2hours 48.5 minutes
                                        '3-0' , '3-12:0', '3-12:30:0'  3days, 3days 12 hours, 3 days 12.5 hours

   --sim-time-minutes FLOAT         What to pass to robin for simulation time-out in minutes

   --sim-time-seconds INT           What to pass to robin for simulation time-out in seconds

   --highest-priority               Not working, due to not having permissions for priority.

   --start-run INT                  Number to start runs at.  For instance, if you stop
                                    the sweeps/simulations and want to come back to them.
                                    Just remember where you left off and enter it here.
                                    Defaults to 1, of course.

   --end-run INT                    Can't see too much of a reason for this but included it
                                    anyway.  Like '--start-run' except this is the number to
                                    end at.  Can use in conjunction with '--start-run'
                                    or not.


"""


from docopt import docopt,DocoptExit
import numpy as np
import os
import sys
import json

import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]


try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)
path = args["--input"].rstrip("/")
basefiles=str(os.path.dirname(os.path.abspath(__file__)))
partition = args["--partition"]
parallelMode = args["--parallel-mode"]
method = args["--method"]
coresPerJob = int(args["--cores-per-job"]) if args["--parallel-mode"] == "sbatch" else False
tasksPerNode=int(args["--tasks-per-node"]) if (args["--parallel-mode"] == "tasks") or (args["--parallel-mode"] == "background") else False
socketStart=int(args["--socket-start"])
myTime="--time {time}".format(time=args["--time"]) if args["--time"] else " "
addToSbatch=args["--add-to-sbatch"] if args["--add-to-sbatch"] else " "
mySimTime=31536000
if args["--sim-time-minutes"]:
    mySimTime=int(np.round(float(args["--sim-time-minutes"])*60))
elif args["--sim-time-seconds"]:
    mySimTime=int(args["--sim-time-seconds"])
priority = 1 if args["--highest-priority"] else 0
startRun=int(args["--start-run"]) if args["--start-run"] else False
endRun=int(args["--end-run"]) if args["--end-run"] else False


socketCount = socketStart
if partition != "False":
    partition = "-p {partition}".format(partition=partition)
else:
    partition = ""
if parallelMode == "sbatch":
    experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/") if os.path.isdir(path+"/"+exp+"/"+i)]
        jobs.sort(key=natural_keys)
        ids = [i for i in os.listdir(path+"/"+exp+"/"+jobs[0]+"/") if os.path.isdir(path+"/"+exp+"/"+jobs[0]+"/"+i)]
        runs =[i for i in os.listdir(path+"/"+exp+"/"+jobs[0]+"/"+ids[0]+"/") if os.path.isdir(path+"/"+exp+"/"+jobs[0]+"/"+ids[0]+"/" + i)]
        runs.sort(key=natural_keys)
        if startRun:
            start=f"Run_{startRun}"
        else:
            start=runs[0]
        if endRun:
            end=f"Run_{endRun}"
        else:
            end=runs[len(runs)-1]
        runs=runs[runs.index(start):runs.index(end)+1]
        for run in runs:
            for job in jobs:
                ids = [i for i in os.listdir(path+"/"+exp+"/"+job+"/") if os.path.isdir(path+"/"+exp+"/"+job+"/"+i)]
                ids.sort(key=natural_keys)
                for ourId in ids:
                    
                    if not(start == 1):
                        cmd="rm {jobPath}/output/*.out".format(jobPath=path+"/"+exp+"/"+job +"/"+ ourId + "/" + run)
                        os.system(cmd)
                    jobPath = path+":PATH:/"+exp+"/"+job +"/"+ ourId + "/" + run
                    baseFilesPath = basefiles
                    command = """source {basefiles}/batsim_environment.sh;sbatch {partition} -N1 -n1 -c{coresPerJob} --export=jobPath='{jobPath}',experiment='{exp}',job='{job}',id='{ourId}',run='{run}',basefiles='{basefiles}',folder='{folder}',priority='{priority}',socketCount={socketCount},myTime={myTime},mySimTime={mySimTime}
                    --output={jobPath}/output/slurm-%j.out --comment='{folder}_{exp}_{job}j_{ourId}i_{run}r' {myTime} {addToSbatch}
                    {basefiles}/experiment.sh {parallelMode} {method}
                    """.format(partition=partition,coresPerJob=coresPerJob,jobPath=jobPath,exp=exp,job=job.rsplit("_",1)[1],ourId=ourId,run=run,basefiles=baseFilesPath,folder=os.path.basename(path),priority=priority,\
                    socketCount=socketCount,myTime=myTime,mySimTime=mySimTime, \
                    parallelMode=parallelMode,method=method,addToSbatch=addToSbatch).replace("\n","")
                    print(command,flush=True)
                    os.system(command)
                    socketCount+=1
elif parallelMode == "tasks":
    #ok we are going to sbatch enough jobs that will each execute --tasks-per-node srun commands
    #but first make sure we know tasks-per-node:
    if tasksPerNode == False:
        print(__doc__)
        print("Error, tasks-per-node was not set yet we are doing parallel-mode = tasks")
        sys.exit(1)
    srunCount=0
    jobPathChString=""
    chPathString=""
    mySimTimeString=""
    jobPathString=""
    experimentString=""
    jobString=""
    ourIdString=""
    runString=""
    socketCountString=""
    experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
    total_sims=0
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/")]
        for job in jobs:
            ids = [i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job+"/"+i)]
            for theId in ids:
                runs = [i for i in os.listdir(path+"/"+exp+"/"+job+"/"+theId) if os.path.isdir(path+"/"+exp+"/"+job + "/" + theId +"/"+ i)]
                total_sims+=len(runs)
    batch_num=1
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/") if os.path.isdir(path+"/"+exp+"/"+i)]
        jobs.sort(key=natural_keys)
        runs.sort(key=natural_keys)
        if startRun:
            start=f"Run_{startRun}"
        else:
            start=runs[0]
        if endRun:
            end=f"Run_{endRun}"
        else:
            end=runs[len(runs)-1]
        runs=runs[runs.index(start):runs.index(end)+1]
        for run in runs:
            for job in jobs:
                ids = [i for i in os.listdir(path+"/"+exp+"/"+job+"/") if os.path.isdir(path+"/"+exp+"/"+job+"/"+i)]
                ids.sort(key=natural_keys)
                for ourId in ids:
                    if not(start == 1):
                        cmd="rm {jobPath}/output/*.out".format(jobPath=path+"/"+exp+"/"+job +"/"+ ourId + "/" + run)
                        os.system(cmd)
                    jobPath = path+":PATH:/"+exp+"/"+job +"/"+ ourId + "/" + run

                    baseFilesPath = basefiles
                    jobPathString=f"{jobPathString} {jobPath}"
                    experimentString=f"{experimentString} {exp}"
                    jobString=f"{jobString} {job.rsplit('_',1)[1]}"
                    ourIdString=f"{ourIdString} {ourId}"
                    runString=f"{runString} {run}"
                    socketCountString=f"{socketCountString} {socketCount}"
                    srunCount+=1
                    total_sims-=1
                    if (srunCount == tasksPerNode) or (total_sims==0):
                        #ok we have reached our limit for a single sbatch, time to sbatch and start another

                        command = """source {basefiles}/batsim_environment.sh;sbatch {partition} -N1 --exclusive --ntasks={tasksPerNode} --export=mySimTime='{mySimTime}',jobPathString='{jobPathString}',experimentString='{experimentString}',jobString='{jobString}',idString='{ourIdString}',runString='{runString}',basefiles='{basefiles}',priority='{priority}',socketCountString='{socketCountString}'
                    {myTime}
                    --output={expPath}/sbatch-{batch_num}.out --comment='{folder}_{batch_num}' {myTime} {addToSbatch}
                    {basefiles}/experiment.sh {parallelMode} {method}
                    """.format(partition=partition,tasksPerNode=tasksPerNode,mySimTime=mySimTime,\
                                jobPathString=jobPathString,experimentString=experimentString,runString=runString,jobString=jobString,ourIdString=ourIdString,\
                                basefiles=basefiles,priority=priority,folder=os.path.basename(path),socketCountString=socketCountString,myTime=myTime,expPath=path,batch_num=batch_num,\
                                parallelMode=parallelMode,method=method,addToSbatch=addToSbatch).replace("\n","")
                        batch_num+=1
                        srunCount=0
                        mySimTimeString=""
                        jobPathString=""
                        experimentString=""
                        jobString=""
                        ourIdString=""
                        runString=""
                        socketCountString=""

                        print(command,flush=True)
                        os.system(command)
                    socketCount+=1
elif parallelMode == "background":
    count = 1
    total_sims=0
    total_count=0
    experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/")]
        for job in jobs:
            ids = [i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job+"/"+i)]
            for theId in ids:
                runs = [i for i in os.listdir(path+"/"+exp+"/"+job+"/"+theId) if os.path.isdir(path+"/"+exp+"/"+job + "/" + theId +"/"+ i)]
                total_sims+=len(runs)
    if total_sims < tasksPerNode:
        tasksPerNode=total_sims
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/") if os.path.isdir(path+"/"+exp+"/"+i)]
        jobs.sort(key=natural_keys)
        #ids = [i for i in os.listdir(path+"/"+exp+"/"+jobs[0]+"/") if os.path.isdir(path+"/"+exp+"/"+jobs[0]+"/"+i)]
        runs =[i for i in os.listdir(path+"/"+exp+"/"+jobs[0]+"/id_1/") if os.path.isdir(path+"/"+exp+"/"+jobs[0]+"/id_1/"+ i)]
        runs.sort(key=natural_keys)
        if startRun:
            start=f"Run_{startRun}"
        else:
            start=runs[0]
        if endRun:
            end=f"Run_{endRun}"
        else:
            end=runs[len(runs)-1]
        runs=runs[runs.index(start):runs.index(end)+1]
        for run in runs:
            for job in jobs:
                ids = [i for i in os.listdir(path+"/"+exp+"/"+job+"/") if os.path.isdir(path+"/"+exp+"/"+job+"/"+i)]
                ids.sort(key=natural_keys)
                for ourId in ids:
                    if not(start == 1):
                        cmd="rm {jobPath}/output/*.out".format(jobPath=path+"/"+exp+"/"+job +"/"+ ourId + "/" + run)
                        os.system(cmd)
                    jobPath = path+":PATH:/"+exp+"/"+job +"/"+ ourId + "/" + run
                    baseFilesPath = basefiles
                    out=jobPath.replace(":PATH:","") +"/output/slurm.out"
                    if (count < tasksPerNode) and (total_count<total_sims):
                        command = f"{baseFilesPath}/experiment.sh {str(parallelMode)} {str(method)} {str(jobPath)} {str(socketCount)} {str(mySimTime)} 2>&1 > {out}  &"
                        count+=1
                        total_count+=1
                    else:
                        command = f"{baseFilesPath}/experiment.sh {str(parallelMode)} {str(method)} {str(jobPath)} {str(socketCount)} {str(mySimTime)} 2>&1 > {out}"
                        count = 1
                        total_count+=1
                    print(command,flush=True)
                    os.system(command) 
                    socketCount+=1 
                              
                    
