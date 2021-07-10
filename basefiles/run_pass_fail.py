"""
Usage:
    run_pass_fail.py [--config=config][--output=output]
    

Options:
    --config=config      configuration file
                         [default: /home/sim/basefiles/1_simulation.config]
                    
    --output=output      output path
                         [default: /home/sim/experiments/simulation1]
    

"""


from docopt import docopt,DocoptExit
import os
import sys
import json
import pandas as pd

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
startRun=False
endRun=False
config=str(args["--config"])
output=str(args["--output"])
command = "python3 /home/sim/basefiles/generate_config.py -i {config} -o {output}".format(config=config, output=output)
os.system(command)
path=output
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
    averages=[]
    for job in jobs:
        
        for number in range(start,end+1,1):
            run = "Run_" + str(number)
            jobPath = path+"/"+exp+"/"+job +"/"+ run
            if not(start == 1):
                cmd="rm {jobPath}/output/*.out".format(jobPath=jobPath)
                os.system(cmd)
            tmpPath = path.split("/",3)
            baseFilesPath = "/" + tmpPath[1] + "/" + tmpPath[2] + "/basefiles"
            command = "python3 /home/sim/basefiles/real_start.py --path {jobpath} --socketCount 28000 ".format(jobpath=jobPath)
            print(command,flush=True)
            os.system(command)
        total = 0
        totalFiles=0
        print("\n\n\n\n")
    
command = "python3 /home/sim/basefiles/aggregate_pass_fail.py --input {output}".format(output=output)
os.system(command)
    
        
        
            
        
    

            


