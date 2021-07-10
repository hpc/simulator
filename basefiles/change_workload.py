"""
Usage: 
     change_workload.py -i FILE --to_csv [-o FILE]
    change_workload.py -i FILE --nodes <INT> [--output FILE --to_csv --scale-widths-based-on INT]
   

Required Options:
    -i FILE --input FILE                where the platform file is
    --nodes <INT>                       change the nb_res to INT
    
Options:                        
    -o FILE --output FILE               where the output workload file should go
                                        [default: input]
                            
    --to_csv                            will output a csv file instead of json
    
    --scale-widths-based-on <INT>       change the widths of jobs based on:
                                        'new_width = old_width * --nodes/INT'                  
"""

from docopt import docopt,DocoptExit
import sys
import numpy as np
import pandas as pd
import json

try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)
nodes=int(args["--nodes"]) if args["--nodes"] else False
toCSV = args["--to_csv"] 
if type(nodes) == bool and args["--scale-widths-based-on"]:
    print(__doc__)
    sys.exit(1)
csvOnly = False
if type(nodes) == bool and toCSV:
    csvOnly = True
    
baseLine=False
if args["--scale-widths-based-on"]:
    baseLine = int(args["--scale-widths-based-on"])
workload_file=args["--input"]
workload_out_file=args["--output"] if not args["--output"] == "input" else args["--input"]

with open(workload_file, "r") as jsonFile:
    data = json.load(jsonFile)

if not csvOnly:
    data["nb_res"] = nodes
    if baseLine:
        for job in data["jobs"]:
            new_width = int(np.ceil(job["res"] * (nodes/baseLine)))
            job["res"]=new_width if new_width <= nodes else new_width -1 
if toCSV:
    df_jobs = pd.DataFrame(data["jobs"])
    df_profiles = pd.DataFrame.from_dict(data["profiles"],orient='index')
    df_profiles["id"] = df_profiles.index
    df_profiles.index = list(range(0,len(df_jobs),1))
    df = df_jobs.merge(df_profiles,on="id")
    with open(workload_out_file,"w") as csvFile:
        df.to_csv(csvFile,sep=",",header=True)
else:
    
    with open(workload_out_file, "w") as jsonFile:
        json.dump(data, jsonFile,indent=4)

