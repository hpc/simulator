"""
Usage:
    make-gannt-chart.py -p FOLDER

Required Options:
    -p FOLDER --path FOLDER             where out_jobs.csv is

"""

from docopt import docopt
import pandas as pd
import os
import sys
import re
from evalys.jobset import JobSet
import matplotlib.pyplot as plt
import matplotlib
args=docopt(__doc__,help=True,options_first=False)
path = args["--path"]
base_folder=path+"/out_jobs.csv"
our_jobs=[]
def mylabel(jobid):
    return ""

matplotlib.rcParams['figure.figsize'] = 80,80
matplotlib.rcParams['figure.dpi']= 300
js = JobSet.from_csv(base_folder)
js.gantt(labeler=mylabel)
plt.savefig(path+"/gantt.png",dpi=300)




