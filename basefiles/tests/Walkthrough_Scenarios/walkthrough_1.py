 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
fig, axs = plt.subplots(1, 1, figsize=(5, 5))

df = pd.read_csv("./total_makespan.csv",header=0,sep=",")

Adf=df.loc[df["exp"]=="1a"]
Bdf=df.loc[df["exp"]=="1b"]
Cdf=df.loc[df["exp"]=="1c"]

plt.plot(Adf["nodes"],Adf["makespan_sec"],label="1a")
plt.plot(Bdf["nodes"],Bdf["makespan_sec"],label="1b")
plt.plot(Cdf["nodes"],Cdf["makespan_sec"],label="1c")
plt.legend()
axs.set_xlabel("nodes")
axs.set_ylabel("makespan")
fig.suptitle("Scenario 1 -- Nodes VS Makespan")
fig.savefig("myplot.png",dpi=600)

