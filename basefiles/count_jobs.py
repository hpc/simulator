#!/usr/bin/env python3
"""
Usage:
  count_jobs.py -i <FILE>
  count_jobs.py --experiment <STR> [--db <PATH> --folder <PATH>]

Required Options 1:
  -i <FILE> --input <FILE>      The workload you would like to count the jobs of

Required Options 2:
  --experiment <STR>            The experiment in the current folder to look up
                                Will use the experiment's parent folder for '--folder'
                                Will use the experiment's root folder to look for '--db'
Optional Options:
  --db                          The database file to look the experiment up in
  --folder                      The folder that the experiment resides in

"""


import json
import os
import pandas as pd
from docopt import docopt,DocoptExit


def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def getParent(myPath,count=1):
    import os
    for i in range(0,count,1):
        myPath = os.path.dirname(myPath)
    return myPath
def countJobs(file):
    InFile = open(file,"r")
    workload = json.load(InFile)
    InFile.close()
    jobs = workload["jobs"]
    count = 0
    for job in jobs:
        if not dictHasKey(job,"purpose"):
            continue
        if job["purpose"] == "reservation":
            count+=1
    return (len(jobs),count,len(jobs)-count)

if __name__ == '__main__':
    try:
        args=docopt(__doc__,help=True,options_first=False)
    except DocoptExit:
        print(__doc__)
        sys.exit(1)
    count = countJobs(args["--input"]) if args["--input"] else False
    if not count:

        #these 3 pieces we need
        db = args["--db"] if args["--db"] else False
        folder = args["--folder"] if args["--folder"] else False
        experiment = args["--experiment"] if args["--experiment"] else False
        #do we have these 3 pieces? if not, get them
        if not db:
            currentDir = os.path.abspath(".")
            db = str(getParent(currentDir))+"/grizzly_workloads_db.csv"
            folder = str(os.path.basename(currentDir))
            basefiles = str(getParent(currentDir,count=3))+"/basefiles"
            #we now have all the info we need
            database = pd.read_csv(db,header=0,sep="|")

            data = database.loc[(database["folder"] == folder) & (database["experiment"] == experiment)]
            filename = data.filename.values[0]
            absPath = basefiles + "/workloads/" + filename
            count = countJobs(absPath)

    print(f"Total Jobs: {count[0]:,}")
    print(f"Total Reservations: {count[1]:,}")
    print(f"Jobs - Reservations: {count[2]:,}")
