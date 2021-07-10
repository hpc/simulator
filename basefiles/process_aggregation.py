"""
Usage:
    process_aggregation.py -i PATH 

Required Options:
    -i PATH --input PATH        where total_makespan.csv lives.  This file
                                should have experiment 1 being the baseline and
                                2,4,8,16,32 coming after

   
"""


from docopt import docopt
import pandas as pd
import os
import sys
import re
from datetime import datetime,timedelta
def atoi(text):
    return int(text) if text.isdigit() else text
    
def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]
        



args=docopt(__doc__,help=True,options_first=False)


path = args["--input"].rstrip("/")

df = pd.read_csv(path,header=0,sep=",")
df2=pd.DataFrame()
makespans=df["makespan_sec"]
makes=[i for i in makespans]
baseline=makes[0]
first=True
calculations=[]
for i in makes:
    if first:
        first=False
        continue
    calculations = calculations.append(i/baseline)
print("Calculations "+str(calculations),flush=True)
    
