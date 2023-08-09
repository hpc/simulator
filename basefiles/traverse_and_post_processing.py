"""
Usage:
    traverse_and_post_process.py -i <path> [--basePath <path>] [--parallel]

Required Options:
    -i, --input <path>    where the experiments are

Optional Options:

    --basePath <path>     where basefiles scripts are
                          [default: scriptPath]

    --parallel            run in parallel(sbatch), otherwise serial
                          [default: False]
   
"""


from docopt import docopt
import os
import sys
import re
def atoi(text):
    return int(text) if text.isdigit() else text
    
def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
        


scriptPath = os.path.expanduser(str(os.path.dirname(os.path.abspath(__file__)))).rstrip("/")
args=docopt(__doc__,help=True,options_first=False)


path = args["--input"].rstrip("/")
basePath = args["--basePath"].rstrip("/")
parallel=args["--parallel"] if args["--parallel"] else False
if basePath == "scriptPath":
    basePath = scriptPath
experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
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
                    runPath = path + "/" + exp + "/" + job + "/" + run
                    cmd = "sbatch -p IvyBridge --export=basePath={},runPath={} --output={}/output/slurm-pp%j.out --comment='pp{}_{}' post_processing_batch.sh".format(basePath,runPath,runPath,exp,job)
                    os.system(cmd)
                elif fileExists:
                    cmd = f"python3 {basePath}/real_start.py --path {path}/{exp}/{job}/{theId}/{run} --method bare-metal --only-output"
                    os.system(cmd)

                


