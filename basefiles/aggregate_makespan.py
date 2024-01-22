#!/usr/bin/env python3
"""
Usage:
    aggregate-makespan.py -i FOLDER [--output FOLDER] [--try-frame1] [--start-run INT] [--end-run INT]

Required Options:
    -i FOLDER --input FOLDER    where the experiments are

Options:
    -o FOLDER --output FOLDER   where the output should go
                                [default: input]

    -t --try-frame1             if we don't find makespan.csv in normal expe-out, then try expe-out_1

    --start-run INT             only include runs starting at start-run
                             
    --end-run INT               only include runs ending at and including end-run
   
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
outPath = args["--input"] if args["--output"] == "input" else args["--output"]
basePath = outPath
rawOutPath = outPath.rstrip("/") + "/raw_total_makespan.csv"
outPath = outPath.rstrip("/") + "/total_makespan.csv"
startRun=args["--start-run"] if args["--start-run"] else 1
endRun=args["--end-run"] if args["--end-run"] else False
tryFrame1=True if args["--try-frame1"] else False
df = pd.DataFrame()
df4 = pd.DataFrame()
df5 = pd.DataFrame()
runs = 1
neCount=0
eCount=0
neCountJob=0
eCountJob=0
expNeCount={}
expECount={}
jobNeCount={}
jobECount={}
totNeCount=0
totECount=0
experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
with open(basePath+"/errors_total_makespan.txt","w") as OutFile:
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/")]
        jobs.sort(key=natural_keys)
        print(exp,flush=True)
        OutFile.write(str(exp)+"\n")
        for job in jobs:
            print(job,flush=True)
            OutFile.write(str(job)+"\n")
            ids = [i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job+"/"+ i)]
            df_fin = pd.DataFrame()
            df_raw_fin = pd.DataFrame()
            for anId in ids:

                runs=len([i for i in os.listdir(path+"/"+exp+"/"+job+"/"+anId) if os.path.isdir(path+"/"+exp+"/"+job + "/" +anId+"/" +i)])
                if endRun:
                    runs=endRun
                if runs > 1:
                    df1 = pd.DataFrame()
                    df3 = pd.DataFrame()
                    neRuns=0
                    for number in range(startRun,runs+1,1):
                        run = "Run_"+ str(number)
                        makespanPath = path+"/"+exp+"/"+job + "/" + anId + "/" + run    + "/output/expe-out/makespan.csv"
                        fileExists=os.path.exists(makespanPath)
                        if not fileExists:
                            if tryFrame1:
                                print("Doesn't Exist: "+makespanPath,flush=True)
                                neRuns+=1
                                makespanPath = path+"/"+exp+"/"+job + "/" + anId + "/" + run    + "/output/expe-out_1/makespan.csv"
                                fileExists = os.path.exists(makespanPath)
                            if not fileExists:
                                print("*** Doesn't Exist: "+makespanPath,flush=True)
                                OutFile.write("Doesn't Exist: "+makespanPath+"\n")
                                neCount+=1
                                neCountJob+=1
                        if fileExists:
                            try:
                                dfTmp = pd.read_csv(makespanPath,sep=",",header=0)
                            except:
                                print("error with file: "+makespanPath,flush=True)
                                OutFile.write("error with file: "+makespanPath+"\n")
                                eCount+=1
                                eCountJob+=1
                                continue
                            dfTmp2 = dfTmp.copy()
                            dfTmp2["run"]=["Run_"+str(number)]
                            dfTmp2["id"]=[anId]
                            dfTmp2["job"]=job
                            dfTmp2["exp"]=exp
                            df1 = pd.concat([df1,dfTmp],axis=0)
                            df3 = pd.concat([df3,dfTmp2],axis=0)
                    print(f"Number Runs don't exist: {neRuns}")            
                    df2 = pd.DataFrame()
                    if len(df1)>0:
                        df2["nodes"] = [df1["nodes"].values[0]]
                        df2["SMTBF"] = [df1["SMTBF"].values[0]]
                        df2["NMTBF"] = [df1["NMTBF"].values[0]]
                        df2["MTTR"] = [df1["MTTR"].values[0]]
                        df2["fixed-failures"] = [df1["fixed-failures"].values[0]]
                        df2["repair-time"] = [df1["repair-time"].values[0]]
                        df2["makespan_sec"] = [df1["makespan_sec"].mean()]
                        df2["avg-avg-pp-slowdown"] = [df1["avg-pp-slowdown"].mean()]
                        df2["avg-pp-slowdown-tau"] = [df1["avg-pp-slowdown-tau"].mean()]
                        df2["avg_tat"] = [df1["avg_tat"].mean()]
                        df2["avg_avg_utilization"] = [df1["avg_utilization"].mean()]
                        avg_waiting = df1["avg_waiting"].mean()
                        sec4 = timedelta(seconds=int(avg_waiting))
                        df2["avg_avg_waiting"]=[df1["avg_waiting"].mean()]
                        df2["avg_avg_waiting_dhms"]=str(sec4)


    
                        sec = timedelta(seconds=(int(df2["makespan_sec"].values[0])))
                        sec2= timedelta(seconds=(int(df2["avg_tat"].values[0])))
                        sec3= timedelta(seconds=(int(df2["avg-avg-pp-slowdown"].values[0])))
                        avg_avg_pp_slowdown_dhms = str(sec3)
                        avg_tat_dhms = str(sec2)
                        makespan_dhms = str(sec)
            
                        df2["makespan_dhms"] = [makespan_dhms]
                        df2["avg_tat_dhms"] = [avg_tat_dhms]
                        df2["avg-avg-pp-slowdown_dhms"]=[avg_avg_pp_slowdown_dhms]
                        df2["AAE"]=[df1["AAE"].mean()]
                        if "checkpointed_num" in df1.columns:
                            df2["checkpointed_num"] = [df1["checkpointed_num"].mean()]
                            if "percent_checkpointed" in df1.columns:
                                df2["percent_checkpointed"] = [df1["percent_checkpointed"].mean()]
                        if "checkpointing_on_num" in df1.columns:
                            df2["checkpointing_on_num"] = [df1["checkpointing_on_num"].mean()]
                            if "checkpointing_on_percent" in df1.columns:
                                df2["checkpointing_on_percent"] = [df1["checkpointing_on_percent"].mean()]   
                        df2["id"]=anId     
                        df2["job"]=job
                        df2["exp"]=exp        
            
                        df = pd.concat([df,df2],axis=0)
                        df4 = pd.concat([df4,df3],axis=0)
                else:
                    makespanPath = path+"/"+exp+"/"+job +"/" +anId +"/Run_1"   + "/output/expe-out/makespan.csv"
                    fileExists = os.path.exists(makespanPath)
                    if not fileExists:
                        print("Doesn't Exist: "+makespanPath, flush=True)
                    if fileExists:
                        dfTmp = pd.read_csv(makespanPath,sep=",",header=0)
                        dfTmp["id"] = anId
                        dfTmp["job"] = job
                        dfTmp["exp"] = exp
                        df = pd.concat([df,dfTmp],axis=0)
                
                jobNeCount[str(exp)+"  "+str(job)]=neCountJob
                jobECount[str(exp)+"  "+str(job)]=eCountJob
                neCountJob=0
                eCountJob=0 
            if len(ids)>1:
                    
                    
                    df5 = pd.concat
            groups=df.groupby(df.exp).groups
            dfavg=pd.DataFrame()


        expNeCount[str(exp)]=neCount
        expECount[str(exp)]=eCount
        totNeCount+=neCount
        totECount+=eCount
        eCount=0
        neCount=0            

    OutFile.write("\n\n\nJob Doesn't Exist: "+str(jobNeCount)+"\n\n\n")
    OutFile.write("Job Error: "+str(jobECount)+"\n\n\n")
    OutFile.write("Doesn't Exist: "+str(expNeCount)+"\n")
    OutFile.write("Error: "+str(expECount)+"\n\n\n")
    OutFile.write("Total Doesn't Exist: "+str(totNeCount)+"\n")
    OutFile.write("Total Error: " +str(totECount)+"\n")
with open(outPath,"w") as OutFile:
    df.to_csv(OutFile,sep=",",header=True)
if runs > 1:
    with open(rawOutPath,"w") as OutFile:
        df4.to_csv(OutFile,sep=",",header=True)

        
