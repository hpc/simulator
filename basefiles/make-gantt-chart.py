#!/usr/bin/env python3
"""
Usage:
    make-gannt-chart.py -p FOLDER [--labels] [--jobs <int> ]

Required Options:
    -p FOLDER --path FOLDER             where out_jobs.csv is
    --labels                            flag to add job labels to graph
                                        can get quite messy if lots of jobs
    --jobs <int>                        The amount of jobs that are not copies
                                        Will use to label which jobs are copies

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
labels= True if args["--labels"] else False
base_folder=path+"/out_jobs.csv"
our_jobs=[]
jobs=int(args["--jobs"]) if args["--jobs"] else False
def myLabelJobs(jobid):
    job = jobid.get("jobID")
    submit = jobid.get("submission_time")
    start = jobid.get("starting_time")
    nodes = len(jobid.get("allocated_resources"))
    finish = jobid.get("finish_time")
    if int(job)>jobs:
        return f"cp:{int(job)-jobs}\nsu:{submit}\nst:{start}\nf:{finish}\nn:{nodes}"
    else:
        return f"{int(job)}\ns:{submit}\nst:{start}\nf:{finish}\nn:{nodes}"
def myLabel(jobid):
    job = jobid.get("jobID")
    submit = jobid.get("submission_time")
    start = jobid.get("starting_time")
    nodes = len(jobid.get("allocated_resources"))
    finish = jobid.get("finish_time")
    return f"{int(job)}\ns:{submit}\nst:{start}\nf:{finish}\nn:{nodes}"
def myNoLabel(jobid):
    return ""

matplotlib.rcParams['figure.figsize'] = 80,80
matplotlib.rcParams['figure.dpi']= 300
js = JobSet.from_csv(base_folder)
if labels:
    if jobs:
        js.gantt(labeler=myLabelJobs)
    else:
        js.gantt(labeler=myLabel)
else:
    js.gantt(labeler=myNoLabel)
plt.savefig(path+"/gantt.png",dpi=300)





