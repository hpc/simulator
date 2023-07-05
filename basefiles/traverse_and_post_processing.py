"""
Usage:
    traverse_and_post_process.py -i <path> --basePath <path>

Required Options:
    -i, --input <path>    where the experiments are
    
    --basePath <path>     where basefiles scripts are
   
"""


from docopt import docopt
import os
import sys
import re
def atoi(text):
    return int(text) if text.isdigit() else text
    
def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
        



args=docopt(__doc__,help=True,options_first=False)


path = args["--input"].rstrip("/")
basePath = args["--basePath"].rstrip("/")
experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
for exp in experiments:
    jobs = [i for i in os.listdir(path+"/"+exp+"/")]
    jobs.sort(key=natural_keys)
    print(exp,flush=True)
    
    for job in jobs:
        print(job,flush=True)
        
        runs = [i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job + "/" + i)]
                    
        for run in runs:
            
            outJobsPath = path + "/" + exp + "/" + job + "/" + run + "/output/expe-out/out_jobs.csv"
            fileExists=os.path.exists(outJobsPath)
            if not fileExists:
                print("Doesn't Exist: "+outJobsPath,flush=True)
                         
            if fileExists:
                runPath = path + "/" + exp + "/" + job + "/" + run
                cmd = "sbatch -p IvyBridge --export=basePath={},runPath={} --output={}/output/slurm-pp%j.out --comment='pp{}_{}' post_processing_batch.sh".format(basePath,runPath,runPath,exp,job)
                os.system(cmd)
                


