 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pathlib
import os
def traverse_project_folder(path,myFunc,inputArgs):
    experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
    for exp in experiments:
        jobs=[i for i in os.listdir(f"{path}/{exp}") if os.path.isdir(f"{path}/{exp}/{i}")]
        for job in jobs:
            ids=[i for i in os.listdir(f"{path}/{exp}/{job}") if os.path.isdir(f"{path}/{exp}/{job}/{i}")]
            for ourId in ids:
                runs=[i for i in os.listdir(f"{path}/{exp}/{job}/{ourId}") if os.path.isdir(f"{path}/{exp}/{job}/{ourId}/{i}")]
                for run in runs:
                    current_run=f"{path}/{exp}/{job}/{ourId}/{run}"
                    pathArgs={"experiments":experiments,"jobs":jobs,"ids":ids,"runs":runs,"path":path,"exp":exp,"job":job,"ourId":ourId,"run":run,"current_run":current_run}
                    inputArgs=myFunc(pathArgs,inputArgs)

    return inputArgs
def myFunc(pathArgs,inputArgs):
    if inputArgs["first"]==True:
        bin_files=[i for i in os.listdir(f"{pathArgs['current_run']}/output/expe-out/bins") if os.path.splitext(i)[1] == ".csv"]
        bins=[os.path.splitext(i)[0].split("_")[1:] for i in bin_files]
        starts=[]
        ends=[]
        avg_waitings={}
        avg_waiting=[]
        for ourBin in bins:
            starts.append(ourBin[0])
            ends.append(ourBin[1])
            df = pd.read_csv(f"{pathArgs['current_run']}/output/expe-out/bins/makespan_{ourBin[0]}_{ourBin[1]}.csv",sep=",",header=0)
            avg_waiting=df["avg_waiting"].values[0]
            avg_waitings[f"{ourBin[0]}_{ourBin[1]}"]=[avg_waiting]
    else:
        bin_files=inputArgs["bin_files"]
        bins=inputArgs["bins"]
        starts=inputArgs["starts"]
        ends=inputArgs["ends"]
        avg_waitings=inputArgs["avg_waitings"]
        for ourBin in inputArgs["bins"]:
            df = pd.read_csv(f"{pathArgs['current_run']}/output/expe-out/bins/makespan_{ourBin[0]}_{ourBin[1]}.csv",sep=",",header=0)
            avg_waiting=df["avg_waiting"].values[0]
            avg_waitings[f"{ourBin[0]}_{ourBin[1]}"].append(avg_waiting)
    inputArgs={"bin_files":bin_files,"bins":bins,"starts":starts,"ends":ends,"avg_waitings":avg_waitings,"first":False}
    return inputArgs




scriptPath = str(pathlib.Path(__file__).parent.absolute())
width=10
height=10
BASE_SECONDS = 1728000000

fig, axs = plt.subplots(1, 1, figsize=(width, height))

df = pd.read_csv("./total_makespan.csv",header=0,sep=",")

exp_1=1 #1 subdivision
exp_2=2 #2 subdivisions
exp_3=4 #4 subdivisions
exp_4=8 #8 subdivisions
experiments=df.job.str.extract(r'experiment_(?P<experiment>\d+)')
experiments["experiment"]=experiments.experiment.astype(int)

df = pd.concat([df,experiments],axis=1)

df["subdivisions"]=2**(df["experiment"]-1)
plt.plot(df["subdivisions"],df["avg_waiting"])
axs.set_xlabel("subdivisions")
axs.set_ylabel("avg waiting time")
axs.set_xticks([1,2,4,8])

axs.set_title("Scenario 3a -- Subdivisions vs Avg Waiting Time")
fig.savefig("myplot.png",dpi=600)


fig, axs = plt.subplots(1, 1, figsize=(width, height))
cmap = plt.get_cmap('hsv')
colors = cmap(np.linspace(0,.75,11))

inputArgs={"first":True}
inputArgs = traverse_project_folder(scriptPath,myFunc,inputArgs)


count=0
for ourBin in inputArgs["bins"]:
    avg_waiting=inputArgs["avg_waitings"][f"{ourBin[0]}_{ourBin[1]}"]
    plt.plot([1,2,4,8],avg_waiting,color=colors[count],label=f"({ourBin[0]},{ourBin[1]}]")
    count+=1

plt.legend(loc="lower right",bbox_to_anchor=(1.2,0.0))
axs.set_xlabel("subdivisions")
axs.set_ylabel("avg waiting time")

axs.set_title("Scenario 3a -- Subdivisions vs Avg Waiting Time By Bin")
axs.set_xticks([1,2,4,8])
fig.savefig("myplot2.png",dpi=600, bbox_inches='tight')


fig, axs = plt.subplots(1, 1, figsize=(width, height))
count=0
for ourBin in inputArgs["bins"]:
    avg_waiting=inputArgs["avg_waitings"][f"{ourBin[0]}_{ourBin[1]}"]
    avg_waiting=avg_waiting/avg_waiting[0]
    plt.plot([1,2,4,8],avg_waiting,color=colors[count],label=f"({ourBin[0]},{ourBin[1]}]")
    count+=1

plt.legend(loc="lower right",bbox_to_anchor=(1.2,0.0))
axs.set_xlabel("subdivisions")
axs.set_ylabel("avg waiting time normalized")

axs.set_title("Scenario 3a -- Subdivisions vs Avg Waiting Time By Bin Normalized")
axs.set_xticks([1,2,4,8])
fig.savefig("myplot3.png",dpi=600, bbox_inches='tight')


