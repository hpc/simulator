"""
Usage: 
    test-checkpointing-batsim.py -i <path>
       
Required Options:
    -i , --input <path>            where the config file is
                         
  
"""





import pandas as pd
import numpy as np
import json
from docopt import docopt
import sys
import os
def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def run_base(file1):
    folder1 = os.path.splitext(file1)[0] + "_test_chkpt_base"
    command = f"myBatchTasks.sh -f {file1} -o {folder1} -m charliecloud -t 20 -s 20000"
"

args=docopt(__doc__,help=True,options_first=False)
OutConfig={}
InConfig = {}
configPath=args["--input"]
with open(configPath,"r") as InFile:
    InConfig = json.load(InFile)

configs=InConfig["configs"]
for config in configs:
    file = config["file"]
    checkpoints = config["checkpoints"]
    start = checkpoints["start"]
    keep = checkpoints["keep"]
    stagger = checkpoints["stagger"]
    count = checkpoints["count"]
    run_base(file)
    for i in range(0,count,1):


    
