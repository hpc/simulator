"""
Usage:
    run-experiments.py -i <FOLDER> [--time INT][--sim-time-minutes FLOAT | --sim-time-seconds INT][--socket-start INT][--single-experiment][--highest-priority][--start-run INT][--end-run INT]

Required Options:
    -i <FOLDER> --input <FOLDER>    Where experiments live

Optional Options:
   --time INT                       The wallclock limit of each submitted job
   
   --sim-time-minutes FLOAT         What to pass to robin for simulation time-out in minutes
   
   --sim-time-seconds INT           What to pass to robin for simulation time-out in seconds
   
   --socket-start INT               Will pass socket numbers to experiment.sh starting at this
                                    number and incrementing by one as needed, not to exceed
                                    60999, AFAIK right now should start at 32768
   --highest-priority               Not working, due to not having permissions for priority.
   
   --start-run INT                  Number to start runs at.  For instance, if you stop
                                    the sweeps/simulations and want to come back to them.
                                    Just remember where you left off and enter it here.
                                    Defaults to 1, of course.

   --end-run INT                    Can't see too much of a reason for this but included it
                                    anyway.  Like '--start-run' except this is the number to
                                    end at.  Can use in conjunction with '--start-run'
                                    or not.
                                                                                    
   --single-experiment			    If true, will only look at jobs in
            					    FOLDER, instead of looking for multiple
			               		    experiments, TODO  hasn't been updated.
					                Don't use this option right now.

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
folder = path.split("/")[len(path.split("/"))-1]
startRun=int(args["--start-run"]) if args["--start-run"] else False
endRun=int(args["--end-run"]) if args["--end-run"] else False
socketCountStart=int(args["--socket-start"]) if args["--socket-start"] else 32768
myTime="--time {time}".format(time=args["--time"]) if args["--time"] else " "
mySimTime=31536000
if args["--sim-time-minutes"]:
    mySimTime=int(np.round(float(args["--sim-time-minutes"])*60))
elif args["--sim-time-seconds"]:
    mySimTime=int(args["--sim-time-seconds"])
socketCount=socketCountStart
priority = 1 if args["--highest-priority"] else 0
single=args["--single-experiment"]
if single:
    exp = path.rsplit("/",1)[1]
    jobs = [i for i in os.listdir(path+"/") if os.path.isdir(path+"/"+i)]
    jobs.sort(key=natural_keys)
    for job in jobs:
        jobPath = path+"/"+job
        tmpPath = path.split("/",3)
        baseFilesPath = "/" + tmpPath[1] + "/" + tmpPath[2] + "/basefiles"
        command = """sbatch --export=jobPath='{jobPath}',experiment='{exp}',job='{job}',baseFilesPath='{basefiles}',folder='{folder}'
        --output={jobPath}/output/slurm-%j.out --comment='{exp}_{job}'
        {jobPath}/experiment.sh
        """.format(jobPath=jobPath,exp=exp,job=job.rsplit("_",1)[1],basefiles=baseFilesPath,folder=folder).replace("\n","")
        os.system(command)
else:
    experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/") if os.path.isdir(path+"/"+exp+"/"+i)]
        jobs.sort(key=natural_keys) 
        runs =len( [i for i in os.listdir(path+"/"+exp+"/"+jobs[0]) if os.path.isdir(path+"/"+exp+"/"+jobs[0]+"/"+ i)])
        if startRun:
            start=startRun
        else:
            start=1
        if endRun:
            end=endRun
        else:
            end=runs
        for number in range(start,end+1,1):
            run = "Run_" + str(number)
            for job in jobs:
                jobPath = path+"/"+exp+"/"+job +"/"+ run
                if not(start == 1):
                    cmd="rm {jobPath}/output/*.out".format(jobPath=jobPath)
                    os.system(cmd)
                tmpPath = path.split("/",3)
                baseFilesPath = "/" + tmpPath[1] + "/" + tmpPath[2] + "/basefiles"
                command = """sbatch -p usrc-nd02 -N1 -n1 -c1 --export=mySimTime={mySimTime},jobPath='{jobPath}',experiment='{exp}',job='{job}',run='{run}',baseFilesPath='{basefiles}',folder='{folder}',priority='{priority}',socketCount={socketCount}
                {myTime}
                --output={jobPath}/output/slurm-%j.out --comment='{folder}_{exp}_{job}_{run}'
                /home/cwalker/basefiles/experiment.sh
                """.format(jobPath=jobPath,exp=exp,run=run,job=job.rsplit("_",1)[1],basefiles=baseFilesPath,folder=folder,priority=priority,socketCount=socketCount,myTime=myTime,mySimTime=mySimTime).replace("\n","")
                print(command,flush=True)
                os.system(command)
                #if socketCount > 65
                socketCount=socketCount+1
                              
