#!/usr/bin/env python3
"""

Will take a log file and make sure what was submitted was also completed.

Usage:
    submit_vs_completed.py -i PATH

Required Options:
    -i PATH --input PATH            where log_file is

"""

import pathlib
import pandas as pd
import json
import re
import sys
scriptPath = str(pathlib.Path(__file__).parent.absolute())
sys.path.append(str(pathlib.Path(scriptPath).parent.absolute()))
from docopt import docopt
args=docopt(__doc__,help=True,options_first=False)
import functions
inputFile = args["--input"]
received_count=0
sending_count=0
regex_Received = re.compile("^.*INFO\| Received \'(.*)\'")
regex_Sending = re.compile("^.*INFO\| Sending \'(.*)\'")
jobs_submitted=set([])
with open(inputFile,"r") as InFile:
    for line in InFile:
        smR = regex_Received.match(line)
        #smS = regex_Sending.match(line)
        if smR != None:
            line_json=json.loads(smR.groups()[0])
            if functions.dictHasKey(line_json,"events"):
                events=line_json["events"]
                for event in events:
                    if event["type"]=="JOB_SUBMITTED":
                        jobs_submitted.add(event["data"]["job_id"])
                    if event["type"]=="JOB_COMPLETED":
                        jobs_submitted.remove(event["data"]["job_id"])
        #if smS != None:
        #    sending_count+=1
#print(f"received: {received_count}")
#print(f"sending: {sending_count}")
print(f"Number not completed: {len(jobs_submitted)}")
print(f"Jobs not completed: {jobs_submitted}")

