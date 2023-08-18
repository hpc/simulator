"""
Usage:
    aggregate-makespan-heatmap.py -p FOLDER [-c FILE] [-o FOLDER] [-b] [--normalize]

Required Options:
    -p FOLDER --path FOLDER             where the experiments are

Options:
    -c FOLDER --concatenate FOLDER      where the old data is (heatmap.csv file)

    -o FOLDER --output FOLDER           where the output should go (graphs and concatenated csv)
                                        [default: path/heatmaps]

    -b --bins                           If set, will calculate from binned data
                                        This assumes you have run post-processing with bins located in output/config.ini
                                        and that it produced output/expe-out/bins/*.csv files

    --normalize                         Will normalize based on the amount of nodes, so 1490 nodes will have a y scale with
                                        the same min/max as 2980 nodes
   
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
def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
        



args=docopt(__doc__,help=True,options_first=False)


path = os.path.abspath(args["--path"].rstrip("/"))
if args["--output"] == "path/heatmaps":
        os.makedirs(f"{path}/heatmaps",exist_ok=True)


outPath = f"{path}/heatmaps" if args["--output"] == "path/heatmaps" else args["--output"]
concat = f"{args['--concatenate']}" if args["--concatenate"] else False
bins = True if args["--bins"] else False
normalize=True if args["--normalize"] else False
basePath = outPath
df_fin = pd.DataFrame()
df_raw_fin = pd.DataFrame()
dictAllSummaryOut = {}
listAllRawOut = []
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
experiments=[i for i in os.listdir(path) if (os.path.isdir(path+"/"+i)) and (i!="heatmaps")]
with open(basePath+"/errors_aggregate_heatmap.txt","w") as OutFile:
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/")]
        jobs.sort(key=natural_keys)
        print(exp,flush=True)
        OutFile.write(str(exp)+"\n")
        for job in jobs:
            print(job,flush=True)
            OutFile.write(str(job)+"\n")
            ids = [i for i in os.listdir(path+"/"+exp+"/"+job) if os.path.isdir(path+"/"+exp+"/"+job+"/"+ i)]

            for anId in ids:

                runs=[int(i.split("_")[1]) for i in os.listdir(path+"/"+exp+"/"+job+"/"+anId) if os.path.isdir(path+"/"+exp+"/"+job + "/" +anId+"/" +i)]
                runs.sort()
                if len(runs) > 0:
                    listDfRuns=[]
                    listDfRaw3=[]
                    #loop bins:
                    def get_runs_concatenated(ourFile,ourPrefix,runs):
                        df1 = pd.DataFrame()
                        df3 = pd.DataFrame()
                        for run in runs:
                            ourPath=f"{ourPrefix}/Run_{run}/output/expe-out/{ourFile}"
                            fileExists = os.path.exists(ourPath)
                            if not fileExists:
                                print(f"Doesn't Exist: {ourPath}")
                            if fileExists:
                                dfTmp = pd.read_csv(ourPath,sep=",",header=0)
                                dfTmp["file"]=[os.path.splitext(os.path.basename(ourFile))[0]]
                                dfTmp2 = dfTmp.copy()
                                dfTmp2["run"]=[f"Run_{run}"]
                                dfTmp2["id"]=[anId]
                                dfTmp2["job"]=job
                                dfTmp2["exp"]=exp
                                
                                #df1 is for summary
                                #df3 is for raw
                                df1 = pd.concat([df1,dfTmp],axis=0)
                                df3 = pd.concat([df3,dfTmp2],axis=0)
                        return df1.copy(),df3.copy()
                    prefix=f"{path}/{exp}/{job}/{anId}"
                    binsFolder=f"{prefix}/Run_{runs[0]}/output/expe-out/bins"                            
                    files=["makespan.csv"]
                    if bins:
                            binFiles=[f"bins/{i}" for i in os.listdir(binsFolder) if os.path.isfile(f"{binsFolder}/{i}")]
                            files.extend(binFiles)
                    for file in files:
                        df1,df3 = get_runs_concatenated(file,prefix,runs)
                        listDfRuns.append(df1)
                        listDfRaw3.append(df3)
                    count=0
                    for aggregate_runs in listDfRuns:
                        summary_out = pd.DataFrame()
                        if len(aggregate_runs)>0:
                            #aggregate_runs contains the raw info of the experiment's runs
                            #summary_out contains the summary
                            summary_out["nodes"] = [aggregate_runs["nodes"].values[0]]
                            summary_out["SMTBF"] = [aggregate_runs["SMTBF"].values[0]]
                            summary_out["NMTBF"] = [aggregate_runs["NMTBF"].values[0]]
                            summary_out["MTTR"] = [aggregate_runs["MTTR"].values[0]]
                            summary_out["fixed-failures"] = [aggregate_runs["fixed-failures"].values[0]]
                            summary_out["repair-time"] = [aggregate_runs["repair-time"].values[0]]
                            summary_out["makespan"] = [aggregate_runs["makespan_sec"].mean()]
                            summary_out["avg-avg-pp-slowdown"] = [aggregate_runs["avg-pp-slowdown"].mean()]
                            #summary_out["avg-pp-slowdown-tau"] = [aggregate_runs["avg-pp-slowdown-tau"].values[0]]
                            summary_out["avg-tat"] = [aggregate_runs["avg_tat"].mean()]
                            summary_out["avg-avg-utilization"] = [aggregate_runs["avg_utilization"].mean()]
                            avg_waiting = aggregate_runs["avg_waiting"].mean()
                            sec4 = timedelta(seconds=int(avg_waiting))
                            summary_out["avg-avg-waiting"]=[avg_waiting]
                            summary_out["avg-avg-waiting_dhms"]=str(sec4)


        
                            sec = timedelta(seconds=(int(summary_out["makespan"].values[0])))
                            sec2= timedelta(seconds=(int(summary_out["avg-tat"].values[0])))
                            sec3= timedelta(seconds=(int(summary_out["avg-avg-pp-slowdown"].values[0])))
                            avg_avg_pp_slowdown_dhms = str(sec3)
                            avg_tat_dhms = str(sec2)
                            makespan_dhms = str(sec)
                
                            summary_out["makespan_dhms"] = [makespan_dhms]
                            summary_out["avg-tat_dhms"] = [avg_tat_dhms]
                            summary_out["avg-avg-pp-slowdown_dhms"]=[avg_avg_pp_slowdown_dhms]
                            summary_out["AAE"]=[aggregate_runs["AAE"].mean()]
                            if "checkpointed_num" in aggregate_runs.columns:
                                summary_out["checkpointed_num"] = [aggregate_runs["checkpointed_num"].mean()]
                                if "percent_checkpointed" in aggregate_runs.columns:
                                    summary_out["percent_checkpointed"] = [aggregate_runs["percent_checkpointed"].mean()]
                            if "checkpointing_on_num" in aggregate_runs.columns:
                                summary_out["checkpointing_on_num"] = [aggregate_runs["checkpointing_on_num"].mean()]
                                if "checkpointing_on_percent" in aggregate_runs.columns:
                                    summary_out["checkpointing_on_percent"] = [aggregate_runs["checkpointing_on_percent"].mean()] 
                            file = aggregate_runs["file"].values[0]  
                            summary_out["id"]=anId     
                            summary_out["job"]=job
                            summary_out["exp"]=exp
                            summary_out["file"]=[file]
                            summary_out["nb_runs"]=[len(aggregate_runs)]
                           
                            if dictHasKey(dictAllSummaryOut,file):
                                summaryBinDf=dictAllSummaryOut[file]
                                summaryBinDf = pd.concat([summaryBinDf,summary_out],axis=0)
                                dictAllSummaryOut[file]=summaryBinDf.copy()
                            else:
                                dictAllSummaryOut[file]=summary_out.copy()
                            df_fin = pd.concat([df_fin,summary_out],axis=0)
                            df_raw_fin = pd.concat([df_raw_fin,listDfRaw3[count]],axis=0)
                            count+=1
    


df_fin = df_fin.reset_index()
df_raw_fin = df_raw_fin.reset_index()
for i in dictAllSummaryOut:
    ourdf = dictAllSummaryOut[i].copy()
    dictAllSummaryOut[i] = ourdf.reset_index()

import re
files=["total_makespan.csv"]
for file in dictAllSummaryOut:
    df = dictAllSummaryOut[file].copy()
    if concat:
        if file == "makespan":
            with open(f"{concat}/total_makespan.csv","r") as InFile:
                df_old = pd.read_csv(InFile,header=0,sep=",")
        else:
            with open(f"{concat}/bins/total_{file}.csv","r") as InFile:
                df_old = pd.read_csv(InFile,header=0,sep=",")
        
        runs_combined=df_old["nb_runs"]+df["nb_runs"]
        for column in ["makespan","avg-avg-pp-slowdown","avg-tat","avg-avg-waiting"]:
            df[column] = ((df[column]*df["nb_runs"])+(df_old[column]*df_old["nb_runs"]))/runs_combined
            dhms_name=f"{column}_dhms"
            df[dhms_name]=pd.to_timedelta(df[column],unit="S").astype(str)
        for column in ["avg-avg-utilization","AAE"]:
            df[column]=((df[column]*df["nb_runs"])+(df_old[column]*df_old["nb_runs"]))/runs_combined
        df["nb_runs"]=runs_combined
    #ok df is now ready to make a heatmap of
    import seaborn as sns
    import matplotlib.pyplot as plt
    import os
    import numpy as np
    heatmaps=[("avg-avg-waiting","Average Queue Waiting Time (seconds)"),("avg-tat","Average Turnaround Time (seconds)"),("avg-avg-utilization","Average Utilization")]
    nodes=df["nodes"].unique()
    if bins:
        os.makedirs(f"{outPath}/bins",exist_ok=True)
    limits={}
    for name,title in heatmaps:
        limits[name]={"min":df[name].min(),"max":df[name].max()}
    for node_num in nodes:
        print(node_num)
        tmp=df.loc[df.nodes==node_num]
        for name,title in heatmaps:
            print(name)
            heatmap=tmp[["SMTBF","MTTR",name]].copy()
            heatmap["SMTBF"]=((1728000000/node_num)/heatmap["SMTBF"].astype(float)).apply(np.floor)
            heatmap["MTTR"]=heatmap["MTTR"]/3600
            heatmap=heatmap.pivot(index="SMTBF",columns="MTTR",values=name)
            heatmap=heatmap.sort_index(ascending=False)
            plt.figure(figsize=(10,10),dpi=300)
            if normalize:
                g = sns.heatmap(heatmap,annot=True,fmt=".4f",vmin=limits[name]["min"],vmax=limits[name]["max"])
            else:
                g = sns.heatmap(heatmap,annot=True,fmt=".4f")
            plt.ylabel("SMTBF Factor")
            plt.xlabel("Mean Time To Repair (hours)")
            if (name == "avg-avg-waiting") or (name == "avg-tat"):
                for t in g.texts: t.set_text(f"{float(t.get_text()):,.0f}")
            else:
                for t in g.texts: t.set_text(f"{float(t.get_text())*100:.2f} %")
            plt.title(title)
            if file == "makespan":
                plt.savefig(f"{outPath}/{node_num}_{name}_heatmap.png",dpi=300)
            else:
                plt.savefig(f"{outPath}/bins/{node_num}_{file}_{name}_heatmap.png",dpi=300)
            plt.close()
    dictAllSummaryOut[file]=df.copy()

for i in dictAllSummaryOut:
    ourdf = dictAllSummaryOut[i].copy()
    if i=="makespan":
        with open(f"{outPath}/total_{i}.csv",'w') as OutFile:
            ourdf.to_csv(OutFile,sep=",",header=True)
    else:
        with open(f"{outPath}/bins/total_{i}.csv",'w') as OutFile:
            ourdf.to_csv(OutFile,sep=",",header=True)
if concat:
    with open(f"{concat}/raw_summary.csv",'r') as InFile:
        df_old = pd.read_csv(InFile,header=0,sep=",")
        df_fin = pd.concat([df_fin,df_old],axis=0)
    with open(f"{concat}/raw.csv",'r') as InFile:
        df_old = pd.read_csv(InFile,header=0,sep=",")
        df_raw_fin = pd.concat([df_raw_fin,df_old],axis=0)
with open(outPath+"/raw_summary.csv","w") as OutFile:
    df_fin.to_csv(OutFile,sep=",",header=True)
with open(outPath+"/raw.csv",'w') as OutFile:
    df_raw_fin.to_csv(OutFile,sep=",",header=True)