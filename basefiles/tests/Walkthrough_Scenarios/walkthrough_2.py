 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

width=8
height=5
BASE_SECONDS = 1728000000

fig, axs = plt.subplots(1, 1, figsize=(width, height))

df = pd.read_csv("./total_makespan.csv",header=0,sep=",")
#change NMTBF to be normalized to BASE_SECONDS.  Example 1x,2x,...,32x
df.loc[:,"NMTBF"]=BASE_SECONDS / df["NMTBF"]

#get a list of failure rates and sort in reverse
NMTBF_times = list(df["NMTBF"].unique())
NMTBF_times.sort(reverse=True)

Adf=df.loc[df["exp"]=="2a"]
Bdf=df.loc[df["exp"]=="2b"]


current_df=Adf
for nmtbf in NMTBF_times:
    nmtbf_df=current_df.loc[current_df["NMTBF"]==nmtbf]
    plt.plot(nmtbf_df["repair-time"],nmtbf_df["avg_waiting"],label=f"{int(nmtbf)}x")
plt.legend()
axs.set_xlabel("repair time(days)")
axs.set_ylabel("avg waiting time")
ticks=list(range(3600*24*2,3600*24*12,3600*24*2))
labels=[f"{i}days" for i in range(2,12,2)]
axs.set_xticks(ticks)
axs.set_xticklabels(labels,rotation=45)
fig.suptitle("Scenario 2a -- repair time VS avg waiting time using fixed repair time")
fig.savefig("myplot.png",dpi=600)

fig, axs = plt.subplots(1, 1, figsize=(width, height))
current_df=Bdf
for nmtbf in NMTBF_times:
    nmtbf_df=current_df.loc[current_df["NMTBF"]==nmtbf]
    plt.plot(nmtbf_df["MTTR"],nmtbf_df["avg_waiting"],label=f"{int(nmtbf)}x")
plt.legend()
axs.set_xlabel("repair time(days)")
axs.set_ylabel("avg waiting time")
ticks=list(range(3600*24*2,3600*24*12,3600*24*2))
labels=[f"{i}days" for i in range(2,12,2)]
axs.set_xticks(ticks)
axs.set_xticklabels(labels,rotation=45)
fig.suptitle("Scenario 2b -- repair time VS avg waiting time using MTTR")
fig.savefig("myplot2.png",dpi=600)



