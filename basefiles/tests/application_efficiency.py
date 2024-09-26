#!/usr/bin/env python3
"""
Usage:
    application_efficiency.py -i <PATH>

Required Options:
    -i <PATH> --input <PATH>    The project folder's full path
"""
import pathlib
import sys
scriptPath = str(pathlib.Path(__file__).parent.absolute())
sys.path.append(str(pathlib.Path(scriptPath).parent.absolute()))
from docopt import docopt, DocoptExit
import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from datetime import datetime,timedelta
try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

path = str(args["--input"])
jobs={}
rows=1
columns=1
width = 10
height =10
cmap = plt.get_cmap('hsv')
colors = cmap(np.linspace(0,1,8))
fig,axs = plt.subplots(rows,columns,figsize=(width,height))
for start,mtbf in zip(range(1,8,1),range(300,1000,100)):
    jobs[mtbf]=[i for i in range(start,287,7)]
count=0
legend_elements=[]
for mtbf in range(900,200,-100):
    mtbf_jobs=jobs[mtbf]
    line_x=[]
    line_y=[]
    theory_x=[]
    theory_y=[]
    for x,job in zip(np.arange(0.1,4.1,0.1),mtbf_jobs):
        df = pd.read_csv(f"{path}/AAE_test/experiment_{job}/id_1/Run_1/output/expe-out/makespan.csv",sep=",",header=0)
        line_x.append(x)
        line_y.append(df["AAE"].values[0])
        m=mtbf
        r=d=2
        c=x*np.sqrt(2*d*m)
        AAE=np.exp(-r/m) * ((c/m)-(d/m))/(np.exp(c/m) -1)
        theory_x.append(x)
        theory_y.append(AAE)
    plt.plot(line_x,line_y,color=colors[count],label=f"{mtbf}x")
    plt.plot(theory_x,theory_y,color=colors[count],linestyle="--")
    legend_elements.append(Line2D([0],[0],color=colors[count],label=f"{mtbf}x"))
    count+=1
legend_elements.append(Line2D([0], [0], color='white',label="Type"))
legend_elements.append(Line2D([0], [0], color='k', label='Actual'))
legend_elements.append(Line2D([0], [0], color='gray', label='Theoretical',linestyle="--"))

plt.legend(handles=legend_elements)
plt.savefig(f"{path}/aae_plot.png",dpi=600)



