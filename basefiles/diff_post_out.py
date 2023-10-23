"""
Usage: 
    diff_post_out.py -i -c
       
Required Options:
    -i , --input <path>            where the post_out_jobs.csv is
    -c , --compare <path>          where the post_out_jobs.csv to compare is
  
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

args=docopt(__doc__,help=True,options_first=False)

input = pd.read_csv(args["--input"])
compare = pd.read_csv(args["--compare"])
