#!/usr/bin/env python3
"""

Get when things happened

Usage:
    get_job_data.py -i PATH -j STR [-l] [-o STR] [-A INT] [-B INT] [-p]

Required Options:
    -i PATH --input PATH            where log_file is (sched.err.log)
    -j STR --job-id STR             the job id to look for
    -l --print-line                 print line
    -p --print-event                print just the job's event
    -B INT --before INT             print this much before the found part of the line (used with --print-line)
    -A INT --after INT              print this much after the found part of the line (used with --print-line)
    -o STR --only STR               only print out STR info ( SUBMIT | EXECUTE | COMPLETED )

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
jobId=args["--job-id"]
jobId=f"w0!{jobId}"
print(jobId)
printLine=True if args["--print-line"] else False
before = int(args["--before"]) if args["--before"] else False
after = int(args["--after"]) if args["--after"] else False
printEvent=True if args["--print-event"] else False
only=args["--only"] if args["--only"] else False
orig_only=only
lookupEvent={"SUBMIT":"JOB_SUBMITTED","EXECUTE":"JOB_EXECUTED","COMPLETED":"JOB_COMPLETED"}
if only:
    try:
        only=lookupEvent[only]
    except:
        print(f"Error: only option {orig_only} not a valid option")
regex_Received = re.compile("^.*INFO\| Received \'(.*)\'")
regex_Sending = re.compile("^.*INFO\| Sending \'(.*)\'")
#job_info={"event":"n/a","line_number":"n/a","line":"n/a"}
job_infos=[]
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
                    if (event["type"]=="EXECUTE_JOB") and (event["data"]["job_id"]==jobId):
                        ex_job_info={"type":"EXECUTE_JOB","time":now,"event":str(event),"line_number":line_number,"line":str(events)}
                        job_infos.append(ex_job_info)
        else:
            smR = regex_Received.match(line)
            if smR != None:
                line_json=json.loads(smR.groups()[0])
                now = float(line_json["now"])
                if functions.dictHasKey(line_json,"events"):
                    events=line_json["events"]
                    for event in events:
                        if (event["type"]=="JOB_SUBMITTED") and (event["data"]["job_id"]==jobId):
                            sub_job_info={"type":"JOB_SUBMITTED","time":now,"event":str(event),"line_number":line_number,"line":str(events)}
                            job_infos.append(sub_job_info)
                        elif (event["type"]=="JOB_COMPLETED") and (event["data"]["job_id"]==jobId):
                            comp_job_info={"type":"JOB_COMPLETED","time":now,"event":str(event),"line_number":line_number,"line":str(events)}
                            job_infos.append(comp_job_info)
                        elif (event["type"]=="JOB_KILLED") and (jobId in event["data"]["job_ids"]):
                            kill_job_info={"type":"JOB_KILLED","time":now,"event":str(event),"line_number":line_number,"line":str(events)}
                            job_infos.append(kill_job_info)
        line_number+=1
for info in job_infos:
    if (not only) or (only == info["type"]):
        print(f"\033[48;5;101mevent:\033[0m {info['type']}")
        print(f"\033[48;5;101mtime:\033[0m  {info['time']}")
        print(f"\033[48;5;101mline#:\033[0m {info['line_number']}")
        if printLine:
            line = info['line']
            line = line.replace(jobId,f"\033[48;5;36m{jobId}\033[0m")
            if before:
                pos = max(0,line.find(jobId)-before)
                line=line[pos:]
            if after:
                pos = min(line.find(jobId)+after,len(line))
                line=line[:pos]
            print(f"\033[48;5;101mline:\033[0m  {line}")
        elif printEvent:
            line = info['line']
            event = info['event']
            pos=line.find(event)

            pos_event=pos
            pos_before=0
            if before:
                pos_before = before
            pos = max(0,pos-pos_before)

            line = line[pos:]
            pos=pos_event+len(event)
            pos_after=0
            if after:
                pos_after=after
            pos = min(len(line),pos+pos_after)

            line = line[:pos]
            line = line.replace(jobId,f"\033[48;5;36m{jobId}\033[0m")
            print(f"\033[48;5;101mline:\033[0m  {line}\n\n")
