"""
Usage: new_plot_tc.py -i PATH [-o PATH] [--with-overlay] [--csv]

Required Options:

-i PATH --input PATH    Where experiments live.  If given the csv option
                        then this is the exact path + filename of csv

Optional Options:

    -o PATH --output PATH   Where to send output    
                            [default: input_path]
                            
    --with-overlay          Will put a theoretical dashed overlay
                            on the graph
                            
    --csv                   Input is a csv file 

                
"""

import pandas as pd
import numpy as np
import seaborn as sns
import math
import matplotlib.pyplot as plt
from docopt import docopt
import os.path
import re
def atoi(text):
    return int(text) if text.isdigit() else text
    
def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

args=docopt(__doc__,help=True,options_first=False)


output = ""
aCSV = args["--csv"]
if aCSV:
    path = args["--input"]
    if args["--output"] == "input_path":
        output = os.path.dirname(args["--input"])
    else:
        output = args["--output"]
else:
    path = args["--input"].rstrip('/')
    if args["--output"] == "input_path":
        output=path
    else:
        output = args["--output"]

overlay = args["--with-overlay"]
if aCSV:
    df_final=pd.read_csv(path,header=0,sep=",")
    exp = os.path.basename(path)
    if overlay:
        uniques=df_final['SMTBF'].unique()
        uniques.sort()
        uniques=uniques[::-1]
        num_SMTBF = len(uniques)
        new_title = 'Application Efficiency vs Checkpoint Interval vs MTBF'
        newx="Error"
        newy="Avg App Efficiency"
        g = sns.relplot(x="x", y="y", kind="line",hue="SMTBF",hue_order=uniques,\
                palette=sns.color_palette(palette="hls", n_colors=num_SMTBF),\
                data=df_final,legend="full",height=9,style='Type').set(\
                                                        title=new_title,xlabel=newx,ylabel=newy)
        leg = g._legend
        leg.set_bbox_to_anchor([1.1, .85])
        plt.axvline(1.0, 0,1,color="black")
        plt.xlabel(newx,fontsize=18)
        plt.ylabel(newy,fontsize=18)
        plt.title(new_title,fontsize=18)
        g.axes[0,0].set_ylim(.60,.95)
        fig = plt.gcf()
        fig.set_size_inches(10,8)
        g.savefig(output+"/"+exp+"_AE_plot.png",dpi=300)
    else:
        uniques=df_final['SMTBF'].unique()
        uniques.sort()
        uniques=uniques[::-1]
        num_SMTBF = len(uniques)
        uniques = uniques.astype('str')
        df_final['SMTBF'] = df_final['SMTBF'].astype('str')
        new_title = 'Application Efficiency vs Checkpoint Interval vs MTBF'
        newx="Error"
        newy="Avg App Efficiency"
        
        g = sns.relplot(x="x", y="y", kind="line",hue="SMTBF",hue_order=uniques,\
                    palette=sns.color_palette(palette="hls", n_colors=num_SMTBF),\
                    data=df_final,legend="full",height=8).set(\
                                                            title=new_title,xlabel=newx,ylabel=newy)
        leg = g._legend
        leg.set_bbox_to_anchor([1.1, .85])
        plt.axvline(1.0, 0,1,color="black")
        g.savefig(output+"/"+exp+"_AE_plot.png",dpi=300)
    
else:
    experiments=[i for i in os.listdir(path) if os.path.isdir(path+"/"+i)]
    for exp in experiments:
        jobs = [i for i in os.listdir(path+"/"+exp+"/")]
        jobs.sort(key=natural_keys)
        print(exp,flush=True)
        df_final=pd.DataFrame()
        for job in jobs:
            myPath=path+"/"+exp+"/"+job+"/Run_1/output/expe-out/avgAE.csv"
            fileExists=os.path.exists(myPath)
            if not fileExists:
                print("Doesn't Exist: " +myPath,flush=True)
            if fileExists:
                tempdf=pd.read_csv(myPath,header=0,sep=",")
                df_final = pd.concat([df_final,tempdf],axis=0,sort=False)
        
        if overlay:
            #set the type (Actual or Theoretical)
            numRows=len(df_final)
            df_final['Type']=["Actual"]*numRows
            
            appEArray = []
            d=2
            R=2
            uniques=df_final['SMTBF'].unique()
            uniques.sort()
            uniques=uniques[::-1]
            num_SMTBF = len(uniques)
            uniqueErrors = df_final['x'].unique()
            uniqueErrors.sort()
            for M in uniques:
                baseTC = math.sqrt(M*d*2)
                
                for error in uniqueErrors:
                    tc = baseTC*error
                    appE = math.exp(-R/M)*(((tc/M)-(d/M))/(math.exp(tc/M)-1))
                    appEArray+=[appE]
                dfTemp = pd.DataFrame({"x":uniqueErrors,"y":appEArray,"SMTBF":[M]*len(appEArray),"Type":["Theoretical"]*len(appEArray)})
                df_final = pd.concat([df_final,dfTemp],axis=0,sort=False)
                appEArray = []
            new_title = 'Application Efficiency vs Checkpoint Interval vs MTBF'
            newx="Error"
            newy="Avg App Efficiency"
            df_final.reset_index(inplace=True)
            with open(output+"/"+exp+"_df_final.csv","w") as OutFile:
                df_final.to_csv(OutFile,sep=",",header=True)
            g = sns.relplot(x="x", y="y", kind="line",hue="SMTBF",hue_order=uniques,\
                    palette=sns.color_palette(palette="hls", n_colors=num_SMTBF),\
                    data=df_final,legend="full",height=9,style='Type').set(\
                                                            title=new_title,xlabel=newx,ylabel=newy)
            leg = g._legend
            leg.set_bbox_to_anchor([1.1, .85])
            plt.axvline(1.0, 0,1,color="black")
            plt.xlabel(newx,fontsize=18)
            plt.ylabel(newy,fontsize=18)
            plt.title(new_title,fontsize=18)
            g.axes[0,0].set_ylim(.60,.95)
            fig = plt.gcf()
            fig.set_size_inches(10,8)
            g.savefig(output+"/"+exp+"_AE_plot.png",dpi=300)
          
        else:
            uniques=df_final['SMTBF'].unique()
            uniques.sort()
            uniques=uniques[::-1]
            num_SMTBF = len(uniques)
            uniques = uniques.astype('str')
            df_final['SMTBF'] = df_final['SMTBF'].astype('str')
            df_final.reset_index(inplace=True)
            with open(output+"/"+exp+"_df_final.csv","w") as OutFile:
                df_final.to_csv(OutFile,sep=",",header=True)
            new_title = 'Application Efficiency vs Checkpoint Interval vs MTBF'
            newx="Error"
            newy="Avg App Efficiency"
            
            g = sns.relplot(x="x", y="y", kind="line",hue="SMTBF",hue_order=uniques,\
                        palette=sns.color_palette(palette="hls", n_colors=num_SMTBF),\
                        data=df_final,legend="full",height=8).set(\
                                                                title=new_title,xlabel=newx,ylabel=newy)
            leg = g._legend
            leg.set_bbox_to_anchor([1.1, .85])
            plt.axvline(1.0, 0,1,color="black")
            g.savefig(output+"/"+exp+"_AE_plot.png",dpi=300)
            
