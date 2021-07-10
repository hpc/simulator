"""
Usage:
    aggregate_pass_fail.py --input PATH

Required Options:
    --input PATH
"""


from docopt import docopt,DocoptExit
import os
import sys
import json
import pathlib
import pandas as pd

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True,
        executable='/bin/bash'
    )
    return process.communicate()[0]
    
try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

path = str(args["--input"]).rstrip("/")
experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
count = 0
runs=0
neCount=0
smallTime=0
failCount=0
jobArray=[]
smallTimeDict={}
countDict={}
failCountDict={}
neCountDict={}
passDict={}
failDict={}
passPercentDict={}
failPercentDict={}
for exp in experiments:
    jobs = [i for i in os.listdir(path+"/"+exp+"/")]
    for job in jobs:
        neCount=0
        smallTime=0
        jobs = [i for i in os.listdir(path+"/"+exp+"/")]
        runs=len([i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job + "/" + i)])
        if runs > 1:
            for number in range(1,runs+1,1):
                run = "Run_"+ str(number)
                passPath=path+"/"+exp+"/"+job+"/"+run+"/output/expe-out/pass_fail.csv"
                fileExists=os.path.exists(passPath)
                if fileExists:
                    df = pd.read_csv(passPath,sep=",",header=0)
                    passOrFail=int(df["pass"].values[0])
                    if passOrFail == -1:
                        smallTime+=1
                    elif passOrFail == 1:
                        count+=1
                    elif passOrFail == 0:
                        failCount+=1
                else:
                    print("file does not exist "+ passPath)
                    neCount+=1
        print("job: "+str(job),flush=True)
        print("Not Enough Time For allowed failures+1 to happen: "+str(smallTime),flush=True)
        print("Pass Fail does not exist for this amount of runs for this job: "+str(neCount),flush=True)
        jobArray.append(job)
        smallTimeDict["{exp} {job}".format(exp=exp,job=job)]=smallTime
        neCountDict["{exp} {job}".format(exp=exp,job=job)]=neCount
        job=0
        smallTime=0
        neCount=0
    print("experiment: "+str(exp),flush=True)
    print("pass: "+str(count)+"     pass percent: "+str(count/float(count+failCount)),flush=True)
    print("fail: "+str(failCount)+"     fail percent: "+str(failCount/float(count+failCount)),flush=True)
    passDict[str(exp)]=count
    failDict[str(exp)]=failCount
    passPercentDict[str(exp)]=count/(count+failCount)
    failPercentDict[str(exp)]=failCount/(count+failCount)
    count=0
    failCount=0
with open(str(path)+"/pass_fail.txt","w") as OutFile:
    OutFile.write("Not Enough Time For allowed failures+1 to happen: \n" + str(smallTimeDict) + "\n\n")
    OutFile.write("Pass Fail Does Not Exist For A Job: \n" + str(neCountDict) + "\n\n\n")
    OutFile.write("Pass Fail Data: \n" + "     Pass:\n"+"        "+str(passDict)+"\n\n"+"     Fail:\n"+"        "+str(failDict)+"\n\n")
    OutFile.write("     Pass Percent: \n" + "        "+str(passPercentDict)+"\n\n" +"     Fail Percent:\n"+"        "+str(failPercentDict))
     
