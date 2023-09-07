"""
Usage:
    traverse_and_post_process.py -i <path> [--basePath <path>] [--parallel-method <string>] [--tasks <int>] [--single] [--bins <string>]

Required Options:
    -i, --input <path>          where the experiments are

Optional Options:

    --basePath <path>           where basefiles scripts are
                                [default: scriptPath]

    --parallel-method <string>  parallel method:
                                none | background | tasks
                                background: will spin up multiple processes by backgrounding
                                tasks: will use SLURM's sbatch/tasks
                                [default: none]

    --tasks <int>               used with --parallel-method: background & tasks
                                background: will use <int> processes at once
                                tasks: will use <int> tasks on each node
                                [default: 1]

    --single                    If set, '--input' represents a single folder inside the main folder
                                so a single 'experiment' (in config file speak) will be done.
                                Useful if each 'experiment' has a different amount of nodes, thus
                                a different set of bins is needed.  Does not help too much if there are
                                jobs with different nodes in a single experiment.

    --bins <string>             post-process, outputing a makespan_<bin> for each bin
                                specified in string where <string> is in format:
                                '[b1,b2,b3,b4]' and produces bins:
                                [b1,b2),[b2,b3),[b3,b4) and 3 makespan_<bin> files
                                If you would like a 4th bin that gathers b4 and greater use a '+'
                                Similarly a '-' at the beginning will gather less than b1:
                                '[-,b1,b2,b3,b4,+]'
                                [default: False]
                          
   
"""


from docopt import docopt
import os
import sys
import re
import json
def atoi(text):
    return int(text) if text.isdigit() else text
    
def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
        


scriptPath = os.path.expanduser(str(os.path.dirname(os.path.abspath(__file__)))).rstrip("/")
args=docopt(__doc__,help=True,options_first=False)


path = args["--input"].rstrip("/")
single = True if args["--single"] else False
basePath = args["--basePath"].rstrip("/")
parallel=args["--parallel-method"] if args["--parallel-method"] != "none" else False
tasks=int(args["--tasks"])
count = 1
bins = args["--bins"] if args["--bins"]!="False" else False
if basePath == "scriptPath":
    basePath = scriptPath
if single:
    experiments = [os.path.basename(path)]
    path = os.path.dirname(path)
else:
    experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i) and i!="heatmaps"]
total_jobs=0
for exp in experiments:
    jobs = [i for i in os.listdir(path+"/"+exp+"/")]
    for job in jobs:
        ids = [i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job+"/"+i)]
        for theId in ids:
            runs = [i for i in os.listdir(path+"/"+exp+"/"+job+"/"+theId) if os.path.isdir(path+"/"+exp+"/"+job + "/" + theId +"/"+ i)]
            for run in runs:
                outJobsPath = f"{path}/{exp}/{job}/{theId}/{run}/output/expe-out/out_jobs.csv"
                if os.path.exists(outJobsPath):
                    total_jobs+=1
total_count=0
for exp in experiments:
    jobs = [i for i in os.listdir(path+"/"+exp+"/")]
    jobs.sort(key=natural_keys)
    print(exp,flush=True)
    
    for job in jobs:
        print(job,flush=True)
        ids = [i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job+"/"+i)]

        for theId in ids:
        
            runs = [i for i in os.listdir(path+"/"+exp+"/"+job+"/"+theId) if os.path.isdir(path+"/"+exp+"/"+job + "/" + theId +"/"+ i)]
                    
            for run in runs:

                outJobsPath = f"{path}/{exp}/{job}/{theId}/{run}/output/expe-out/out_jobs.csv"
                fileExists=os.path.exists(outJobsPath)
                if not fileExists:
                    print("Doesn't Exist: "+outJobsPath,flush=True)

                if fileExists and parallel:
                    if bins:
                        with open(f"{path}/{exp}/{job}/{theId}/{run}/output/config.ini","r") as IOFile:
                            config=json.load(IOFile)
                        with open(f"{path}/{exp}/{job}/{theId}/{run}/output/config.ini","w") as IOFile:
                            config["bins"]=bins
                            json.dump(config,IOFile,indent=4)
                    if parallel == "background":
                            if (count < tasks) and (total_count<total_jobs):
                                cmd = f"python3 {basePath}/real_start.py --path {path}/{exp}/{job}/{theId}/{run} --method bare-metal --only-output &"
                                count+=1
                                total_count+=1
                            else:
                                cmd = f"python3 {basePath}/real_start.py --path {path}/{exp}/{job}/{theId}/{run} --method bare-metal --only-output"
                                count = 1
                                total_count+=1
                            os.system(cmd)
                    if parallel == "tasks":
                        cmd = "sbatch -p IvyBridge --export=basePath={},runPath={} --output={}/output/slurm-pp%j.out --comment='pp{}_{}' post_processing_batch.sh".format(basePath,f"{path}/{exp}/{job}/{theId}/{run}",exp,job)
                        os.system(cmd)
                elif fileExists:
                    if bins:
                        with open(f"{path}/{exp}/{job}/{theId}/{run}/output/config.ini","r") as IOFile:
                            config=json.load(IOFile)
                        with open(f"{path}/{exp}/{job}/{theId}/{run}/output/config.ini","w") as IOFile:
                            config["bins"]=bins
                            json.dump(config,IOFile,indent=4)
                    cmd = f"python3 {basePath}/real_start.py --path {path}/{exp}/{job}/{theId}/{run} --method bare-metal --only-output"
                    os.system(cmd)

                




                


