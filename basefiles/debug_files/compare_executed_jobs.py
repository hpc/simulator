#!/usr/bin/env python3
"""

Will take an original log file and get all allocations of jobs in it
Then will compare the input log file and return the first job that is not the same as original

Usage:
    compare_executed_jobs.py -o PATH -i PATH

Required Options:
    -o PATH --original PATH         Where the original log file is

    -i PATH --input PATH            Where the log file to compare to the original is

"""
import pathlib
import pandas as pd
import json
import re
import sys
import os
scriptPath = str(pathlib.Path(__file__).parent.absolute())
sys.path.append(str(pathlib.Path(scriptPath).parent.absolute()))
from docopt import docopt
args=docopt(__doc__,help=True,options_first=False)
import functions
inputFile = args["--input"]
originalFile = args["--original"]

regex_Received = re.compile("^.*INFO\| Received \'(.*)\'")
regex_Sending = re.compile("^.*INFO\| Sending \'(.*)\'")
original_jobs={}
jobs={}
with open(originalFile,"r") as InFile:
    count = 1
    for line in InFile:
        smR = regex_Sending.match(line)
        #smS = regex_Sending.match(line)
        if smR != None:
            line_json=json.loads(smR.groups()[0])
            now=line_json["now"]
            if functions.dictHasKey(line_json,"events"):
                events=line_json["events"]
                for event in events:
                    if event["type"]=="EXECUTE_JOB":
                        original_jobs[event["data"]["job_id"]]=[event["data"]["alloc"],count,now]
        count+=1
not_same=False
with open(inputFile,"r") as InFile:
    count = 1
    for line in InFile:
        smR = regex_Sending.match(line)
        #smS = regex_Sending.match(line)
        if smR != None:
            line_json=json.loads(smR.groups()[0])
            now = line_json["now"]
            if functions.dictHasKey(line_json,"events"):
                events=line_json["events"]
                for event in events:
                    if event["type"]=="EXECUTE_JOB":
                        job_id=event["data"]["job_id"]
                        orig_job_id = job_id.split("$")[0]
                        alloc = event["data"]["alloc"]
                        orig_alloc = original_jobs[orig_job_id][0]
                        line_number= original_jobs[orig_job_id][1]
                        orig_time = original_jobs[orig_job_id][2]
                        if alloc != orig_alloc:
                            print(f"job_id:{job_id}\norig_alloc:{orig_alloc}\nalloc:{alloc}\norig_line:{line_number:,}\nline:{count:,}\norig_time:{orig_time:,}\ntime:{now:,}")
                            not_same=True
                            break
                if not_same:
                    break
        count+=1

