#!/usr/bin/env python3
"""

Will take a log file and a machine number and tell you what job got allocated that machine number

Usage:
    which_job_allocated.py -i PATH -m INT [-t INT] [-s INT] [-n INT]

Required Options:
    -i PATH --input PATH            The path to the log file

    -m INT --machine INT            The machine number to search for

    -t FLOAT --time FLOAT           Simulated time at which this machine was allocated

    -s INT --start INT              More than one job was probably assigned this machine.
                                    In order, which allocation do you want to start at.
                                    [default: 1]
    -n INT --number                 More than one job was probably assigned this machine.
                                    How many allocations from the start do you want to print.
                                    '-1' = all
                                    [default: -1]


"""
import pathlib
import pandas as pd
import json
import re
import sys
import os
scriptPath = str(pathlib.Path(__file__).parent.absolute())
sys.path.append(str(pathlib.Path(scriptPath).parent.absolute()))
import intervalset
from docopt import docopt
args=docopt(__doc__,help=True,options_first=False)
import functions
inputFile = args["--input"]
machine = int(args["--machine"])
start=int(args["--start"])
number_to_print=int(args["--number"])
time=float(args["--time"])
if time != None:
    number_to_print=-1
    start=1
time_last_allocated = job_last_allocated = alloc_last_allocated = job_line_number = 0

regex_Received = re.compile("^.*INFO\| Received \'(.*)\'")
regex_Sending = re.compile("^.*INFO\| Sending \'(.*)\'")
original_jobs={}
jobs={}
with open(inputFile,"r") as InFile:
    line_number = 1
    num_found=0
    num_printed=0
    for line in InFile:
        smR = regex_Sending.match(line)
        #smS = regex_Sending.match(line)
        if smR != None:
            line_json=json.loads(smR.groups()[0])
            now = float(line_json["now"])
            if functions.dictHasKey(line_json,"events"):
                events=line_json["events"]
                for event in events:
                    if event["type"]=="EXECUTE_JOB":
                        job_id = event["data"]["job_id"]
                        job_alloc = event["data"]["alloc"]
                        if (time != None) and ( now >= time):
                            print(f"job:{job_last_allocated}\nalloc:{alloc_last_allocated}\nline:{job_line_number:,}\ntime:{time_last_allocated}")
                            sys.exit(0)
                        if intervalset.from_intervalset_to_list(job_alloc).count(machine) == 1:
                            num_found+=1
                            if (time != None) and (now < time):
                                time_last_allocated = now
                                job_last_allocated = job_id
                                alloc_last_allocated = job_alloc
                                job_line_number = line_number
                            if (num_found >= start) and (time == None):
                                print(f"job:{job_id}\nalloc:{job_alloc}\nline:{line_number:,}")
                                num_printed+=1
                            if (num_printed >= number_to_print) and (number_to_print != -1):
                                sys.exit(0)
        line_number+=1
sys.exit(1)
