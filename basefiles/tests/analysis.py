#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mtplt
import os
import seaborn as sns
import warnings
import json
import sys
import numpy as np


usage="""
Usage:
    python3 analysis.py --folder /path/to/simulator/experiments/paper ( --all | --outliers | --non-outliers |--comparisons )
    python3 analysis.py --help
Required:
    --folder            absolute path to the folder where the simulation's data for paper.config was output to

Required Option: (choose one)
    --all               output all graphs

    --outliers          output only graphs including outliers, plus comparisons

    --non-outliers      output only graphs with non-outliers, plus comparisons

    --comparisons       output only comparison graphs (much faster)

"""

scriptPath=str(os.path.dirname(os.path.abspath(__file__)))
output_folder=f"{scriptPath}/paper_analysis/"



if sys.argv[1]=="--help":
    print(usage)
    sys.exit(1)
if (len(sys.argv) != 4) or (sys.argv[1] != "--folder"):
    print(usage)
    sys.exit(1)
if not os.path.exists(sys.argv[2]):
    print(f"folder: {sys.argv[2]} : folder not found")
    sys.exit(1)
if not (sys.argv[3] in [ "--all", "--outliers", "--non-outliers" , "--comparisons" ] ):
    print(f" last option to analysis.py not valid: {sys.argv[3]}")
    sys.exit(1)
else:
    graph_option=sys.argv[3]

    folder1=sys.argv[2]
    database = pd.read_csv(folder1+"/grizzly_workloads_db.csv",header=0,sep="|")
    bins = [0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047]
    import json
    def toJson(x):
        return json.loads(x)
    database["reservation-json"].apply(toJson)
    times = []
    subdivisions=[]
    subdivision_units=[]
    for index, row in database.iterrows():
        times.append(json.loads(row["reservation-json"])["reservations-array"][0]["time"])
        subdivisions.append(json.loads(row["reservation-json"])["reservations-array"][0]["subdivisions"])
        subdivision_units.append(json.loads(row["reservation-json"])["reservations-array"][0]["subdivisions-unit"])

    database["time"]=times
    database["subdivisions"]=subdivisions
    database["subdivisions-unit"]=subdivision_units
    database_orig = database.copy()

    metric = "total_waiting_time"

    #first load the out_jobs:
    metrics = {"total_waiting_time":"Time","pp_slowdown":"Number"}
    metricType = metrics[metric]
    mean_color="cyan"
    count=0
    all_binned_means=[]
    all_binned_maxs=[]
    all_binned_stds=[]
    all_binned_avg_maxs=[]
    all_binned_avg_mins=[]
    all_overall_mean=[]
    all_overall_max=[]
    all_overall_min=[]
    all_overall_avg_max=[]
    all_overall_avg_min=[]
    all_overall_std=[]
    def myAnnotate(myplot,dictValues):

        myBGColor = (.52, .52, .52)
        mean_color = "cyan"
        max_color = (.8, 0, .22)
        min_color = (.3, .8, .3)
        max_avg_color = (.8,0,.5)
        min_avg_color = (.3,.8,.6)
        std_color = (.9, .7, .3)
        overall_data_xy =(1.025,-.1)

        overall_data_xycoords="axes fraction"
        overall_data_fontsize=15
        myFontSizeLabel=15
        overall_data_fontfamily="monospace"
        overall_data_textcoords="offset pixels"
        fontweights=[700]
        datapoint_height = 100
        bias3 = 350
        if metric == "pp_slowdown":
            overall_data_xy = (1.025,-.074)
            bias4 = 120
        else:
            bias4 = 100
        def overall_data_xytext(datapoint):
            return (700,-datapoint*datapoint_height)
        def overall_data_xylabel(datapoint):
            return (0,-datapoint*datapoint_height)
        def binned_data_xytext(datapoint):
            return (-270,-datapoint*datapoint_height - bias3)
        def binned_data_xylabel(datapoint):
            return (0,-datapoint*datapoint_height + bias4)
        datapoint = 2
        myWidth = ""
        myLabelWidth = "16s"
        def myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor):

            myplot.annotate(text="{}".format(symbol_text),
                        xy=overall_data_xy,
                        xycoords=overall_data_xycoords,
                        xytext=overall_data_xytext(datapoint),
                        fontsize=overall_data_fontsize+1,
                        fontweight=1000,
                        fontfamily=overall_data_fontfamily,
                        textcoords=overall_data_textcoords)
            myplot.annotate(text="{:{}}".format(myText,myWidth),
                        xy=overall_data_xy,
                        xycoords=overall_data_xycoords,
                        xytext=overall_data_xytext(datapoint),
                        fontsize=overall_data_fontsize,
                        fontfamily=overall_data_fontfamily,
                        textcoords=overall_data_textcoords)
            myText = "Overall Mean"
            myplot.annotate(text="{:{}}".format(myLabel,myLabelWidth),
                        xy=overall_data_xy,
                        xycoords=overall_data_xycoords,
                        xytext=overall_data_xylabel(datapoint),
                        color=myColor,
                        backgroundcolor=myBGColor,
                        fontsize=myFontSizeLabel,
                        fontfamily="monospace",
                        fontweight=fontweights[0],
                        textcoords=overall_data_textcoords)


        myText = dictValues['mean_overall_text']
        myLabel = "Overall Mean"
        myColor = mean_color
        symbol_text="μ="
        myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
        datapoint += 1

        myText = dictValues['max_overall_text']
        myLabel = "Overall Max"
        myColor = max_color
        symbol_text = "↑="
        myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
        datapoint += 1

        myText = dictValues['min_overall_text']
        myLabel = "Overall Min"
        myColor = min_color
        symbol_text = "↓="
        myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
        datapoint += 1

        myText = dictValues['max_avg_overall_text']
        myLabel = "Overall Avg Max"
        myColor = max_avg_color
        symbol_text="↥="
        myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
        datapoint += 1

        myText = dictValues['min_avg_overall_text']
        myLabel = "Overall Avg Min"
        myColor = min_avg_color
        symbol_text="↧="
        myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
        datapoint += 1

        myText = dictValues['std_overall_text']
        myLabel = "Overall Std"
        myColor = std_color
        symbol_text="σ="
        myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
        datapoint += 2
        if metricType == "Time":
            values = []
            for i in ["myOverallStd","myOverallMin","myOverallMax","myOverallAvgMax","myOverallAvgMin","myOverallMean"]:
                i=dictValues[i]
                if i > 24*3600:
                    i=f"{i/(24*3600):10,.2f} days"
                elif i > 3600:
                    i=f"{i/(3600):10,.2f}  hrs"
                elif i > 60:
                    i=f"{i/(60):10,.2f}  min"
                else:
                    i=f"{i:10,.2f}  sec"
                values.append(i)

            myFormat = "13s"
            dictValues["std_overall_text"] = "{:{}}".format(values[0],myFormat)
            dictValues["min_overall_text"] = "{:{}}".format(values[1],myFormat)
            dictValues["max_overall_text"] = "{:{}}".format(values[2],myFormat)
            dictValues["max_avg_overall_text"] = "{:{}}".format(values[3],myFormat)
            dictValues["min_avg_overall_text"] = "{:{}}".format(values[4],myFormat)
            dictValues["mean_overall_text"] = "{:{}}".format(values[5],myFormat)

            myText = dictValues['mean_overall_text']
            myLabel = "Overall Mean"
            myColor = mean_color
            symbol_text="μ="
            myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
            datapoint += 1

            myText = dictValues['max_overall_text']
            myLabel = "Overall Max"
            myColor = max_color
            symbol_text = "↑="
            myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
            datapoint += 1

            myText = dictValues['min_overall_text']
            myLabel = "Overall Min"
            myColor = min_color
            symbol_text = "↓="
            myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
            datapoint += 1

            myText = dictValues['max_avg_overall_text']
            myLabel = "Overall Avg Max"
            myColor = max_avg_color
            symbol_text="↥="
            myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
            datapoint += 1

            myText = dictValues['min_avg_overall_text']
            myLabel = "Overall Avg Min"
            myColor = min_avg_color
            symbol_text="↧="
            myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)
            datapoint += 1

            myText = dictValues['std_overall_text']
            myLabel = "Overall Std"
            myColor = std_color
            symbol_text="σ="
            myAnnotateOverall(datapoint,myText,myLabel,symbol_text,myColor)

        count_arr = dictValues["count_arr"]
        binned_means = dictValues["binned_means"]
        binned_maxs = dictValues["binned_maxs"]
        binned_mins = dictValues["binned_mins"]
        binned_avg_maxs = dictValues["binned_avg_maxs"]
        binned_avg_mins = dictValues["binned_avg_mins"]
        binned_stds = dictValues["binned_stds"]


        for iter in range(0, 11, 1):
            datapoint = 0
            n = count_arr[iter]
            mu = binned_means[iter]
            myMax = binned_maxs[iter]
            myMin = binned_mins[iter]
            myAvgMax = binned_avg_maxs[iter]
            myAvgMin = binned_avg_mins[iter]
            myStd = binned_stds[iter]
            binned_label_xy = (-.1,-.12)
            if metric == "pp_slowdown":
                overall_data_xy = (-.08,-.08)
            binned_label_xycoords= "axes fraction"
            binned_label_fontsize= 15
            binned_label_fontfamily="monospace"
            binned_label_textcoords = "offset pixels"
            binned_data_xy =(iter,0)
            binned_data_xycoords="data"
            binned_data_fontsize=14
            binned_data_fontfamily="monospace"
            binned_data_textcoords = "offset pixels"
            myFontSizeLabel=15
            myLabelWidth= 13
            myFormat = "15,.2f"
            std_binned_text = "{:{}}".format(myStd,myFormat)
            min_binned_text = "{:{}}".format(myMin,myFormat)
            max_binned_text = "{:{}}".format(myMax,myFormat)
            avg_max_binned_text = "{:{}}".format(myAvgMax,myFormat)
            avg_min_binned_text = "{:{}}".format(myAvgMin,myFormat)
            mean_binned_text = "{:{}}".format(mu,myFormat)

            fontweights=[700,1000]
            nText = f"n={n:7,}"
            myNum = int(5/2)
            myBlankFormat = f"{myNum}"
            myNFormat = f"{len(nText)}"

            myplot.annotate(text="{:{}}{:{}}".format(" ",myBlankFormat,nText,myNFormat),
                            xy=binned_data_xy,
                            xycoords=binned_data_xycoords,
                            xytext=binned_data_xytext(datapoint),
                            fontsize=18,
                            fontfamily=binned_data_fontfamily,
                            fontweight=700,
                            textcoords = binned_data_textcoords)
            datapoint+=2
            def binned_annotate(datapoint,data_text,label_text,symbol_text,myColor):
                myplot.annotate(text=symbol_text,
                            xy=binned_data_xy,
                            xycoords = binned_data_xycoords,
                            xytext = binned_data_xytext(datapoint),
                            fontsize=binned_data_fontsize+1,
                            fontweight=fontweights[1],
                            fontfamily=binned_data_fontfamily,
                            textcoords = binned_data_textcoords)
                myplot.annotate(text=data_text,
                            xy=binned_data_xy,
                            xycoords=binned_data_xycoords,
                            xytext=binned_data_xytext(datapoint),
                            fontsize=binned_data_fontsize,
                            fontfamily=binned_data_fontfamily,
                            textcoords = binned_data_textcoords)


                myplot.annotate(text="{:{}}".format(label_text,myLabelWidth),
                                xy=binned_label_xy,
                                xycoords=binned_label_xycoords,
                                xytext=binned_data_xylabel(datapoint),
                                color=myColor,
                                backgroundcolor=myBGColor,
                                fontsize=myFontSizeLabel,
                                fontfamily=binned_label_fontfamily,
                                fontweight=fontweights[0],
                                textcoords=binned_label_textcoords)
            myText = "Bin Mean:"
            myColor = mean_color
            dataText = mean_binned_text
            symbol_text="μ="
            binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
            datapoint+=1


            myText = "Bin Max:"
            myColor = max_color
            dataText = max_binned_text
            symbol_text = "↑="
            binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
            datapoint+=1

            myText = "Bin Min:"
            myColor = min_color
            dataText = min_binned_text
            symbol_text = "↓="
            binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
            datapoint+=1

            myText = "Bin Avg Max:"
            myColor = max_avg_color
            dataText = avg_max_binned_text
            symbol_text="↥="
            binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
            datapoint+=1

            myText = "Bin Avg Min:"
            myColor = min_avg_color
            dataText = avg_min_binned_text
            symbol_text="↧="
            binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
            datapoint+=1

            myText = "Bin Std:"
            myColor = std_color
            dataText = std_binned_text
            symbol_text="σ="
            binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
            datapoint+=2
            if metricType =="Time":
                values=[]
                for i in [myStd,myMin,myMax,myAvgMax,myAvgMin,mu]:
                    if i > 24*3600:
                        i=f"{i/(24*3600):10,.2f} days"
                    elif i > 3600:
                        i=f"{i/(3600):10,.2f}  hrs"
                    elif i > 60:
                        i=f"{i/(60):10,.2f}  min"
                    else:
                        i=f"{i:10,.2f}  sec"
                    values.append(i)
                myFormat = "15s"
                std_binned_text = "{:{}}".format(values[0],myFormat)
                min_binned_text = "{:{}}".format(values[1],myFormat)
                max_binned_text = "{:{}}".format(values[2],myFormat)
                avg_max_binned_text = "{:{}}".format(values[3],myFormat)
                avg_min_binned_text = "{:{}}".format(values[4],myFormat)
                mean_binned_text = "{:{}}".format(values[5],myFormat)

                myText = "Bin Mean:"
                myColor = mean_color
                dataText = mean_binned_text
                symbol_text="μ="
                binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
                datapoint+=1

                myText = "Bin Max:"
                myColor = max_color
                dataText = max_binned_text
                symbol_text = "↑="
                binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
                datapoint+=1

                myText = "Bin Min:"
                myColor = min_color
                dataText = min_binned_text
                symbol_text = "↓="
                binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
                datapoint+=1

                myText = "Bin Avg Max:"
                myColor = max_avg_color
                dataText = avg_max_binned_text
                symbol_text="↥="
                binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
                datapoint+=1

                myText = "Bin Avg Min:"
                myColor = min_avg_color
                dataText = avg_min_binned_text
                symbol_text="↧="
                binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
                datapoint+=1

                myText = "Bin Std:"
                myColor = std_color
                dataText = std_binned_text
                symbol_text="σ="
                binned_annotate(datapoint,dataText,myText,symbol_text,myColor)
                datapoint+=3
                arrowprops = {'width': .5, 'headwidth': 1, 'headlength': 1, 'shrink':.12}
                my_xy=binned_data_xytext(datapoint)
                my_y =my_xy[1]
                if iter == 0:
                    continue
                myplot.annotate(text="",
                            xy=(iter-.5,0),
                            xycoords=binned_data_xycoords,
                            xytext=(0,my_y),
                            fontsize=15,
                            fontfamily="monospace",
                            textcoords="offset pixels",
                            arrowprops = arrowprops)

    def plotMyGraphs(cutOutliersTF=True,pp_slowdown=60,data_also=False,data_only=False,runs=[1,1]):
        global database
        global folder1
        for index, row in database.iterrows():
            row = row.copy()
            print(index,end="")
            print(":  ",end="")
            exp = row["experiment"]
            folder2="/grizzly_2018_resv"
            full_df = pd.DataFrame()
            dfList=[]
            for run in range(runs[0],runs[1]+1,1):
                rel_path = f"/id_1/Run_{run}/output/expe-out"
                full_path = folder1+folder2+"/"+exp+rel_path+"/post_out_jobs.csv"
                if not os.path.exists(full_path):
                #    all_binned_means.append([0]*len(bins))
                #    all_binned_maxs.append([0]*len(bins))
                #    all_binned_stds.append([0]*len(bins))
                #    all_binned_avg_maxs.append([0]*len(bins))
                #    all_binned_avg_mins.append([0]*len(bins))
                #    all_overall_mean.append(0)
                #    all_overall_max.append(0)
                #    all_overall_min.append(0)
                #    all_overall_avg_max.append(0)
                #    all_overall_avg_min.append(0)
                #    all_overall_std.append(0)
                    continue
                dfList.append(pd.read_csv(full_path,header=0,sep=","))
                print(f" {run}",end="")
            full_df = pd.concat(dfList, axis=0, ignore_index=True)

            print("")


            tau = pp_slowdown

            def pp_slowdown_apply(x):
                return max((x.total_waiting_time + x.total_execution_time)/(x.requested_number_of_resources * max(x.total_execution_time,60)),1)
            full_df = full_df.loc[full_df["purpose"]!="reservation"]

            if metric == "pp_slowdown":
                full_df["pp_slowdown"] = full_df.apply(pp_slowdown_apply,axis="columns")

            full_df['binned'] = pd.cut(full_df['requested_number_of_resources'], bins)

            full_df["folder"]=[folder1]*len(full_df)
            job_df = full_df.loc[full_df.purpose == "job"]
            resv_df = full_df.loc[full_df.purpose == "reservation"]
            df = full_df

            count_arr = df.groupby('binned').count().job_id.values
            binned_means = df.groupby('binned').mean()[metric].values
            binned_maxs = df.groupby('binned').max()[metric].values

            binned_mins = df.groupby('binned').min()[metric].values
            binned_stds = df.groupby('binned').std()[metric].values
            binned_avg_maxs = df.groupby(['folder','binned']).max()[metric].values
            binned_avg_mins = df.groupby(['folder','binned']).min()[metric].values
            df.groupby('binned')

            myOverallMean = df[metric].mean()
            myOverallMax = df[metric].max()
            myOverallMin = df[metric].min()
            myOverallAvgMax = df.groupby(['folder']).max()[metric].mean()
            myOverallAvgMin = df.groupby(['folder']).min()[metric].mean()
            myOverallStd = df[metric].std()
            count_bins_displayed = sum([1 for i in count_arr if i > 0])
            if cutOutliersTF:
                cutOutliers = myOverallMean+myOverallStd+myOverallStd
            else:
                cutOutliers = myOverallMax
            if (data_also==True) or (data_only==True):
                all_binned_means.append(binned_means)
                all_binned_maxs.append(binned_maxs)
                all_binned_stds.append(binned_stds)
                all_binned_avg_maxs.append(binned_avg_maxs)
                all_binned_avg_mins.append(binned_avg_mins)
                all_overall_mean.append(myOverallMean)
                all_overall_max.append(myOverallMax)
                all_overall_min.append(myOverallMin)
                all_overall_avg_max.append(myOverallAvgMax)
                all_overall_avg_min.append(myOverallAvgMin)
                all_overall_std.append(myOverallStd)

                if data_only == True:
                    continue

            dictValues={}
            dictValues.update({"std_overall_text": f"{myOverallStd:15,.2f}"})
            dictValues.update({"min_overall_text": f"{myOverallMin:15,.2f}"})
            dictValues.update({"max_overall_text": f"{myOverallMax:15,.2f}"})
            dictValues.update({"max_avg_overall_text" : f"{myOverallAvgMax:15,.2f}"})
            dictValues.update({"min_avg_overall_text" :f"{myOverallAvgMin:15,.2f}"})
            dictValues.update({"mean_overall_text": f"{myOverallMean:15,.2f}"})
            dictValues.update({"myOverallStd":myOverallStd})
            dictValues.update({"myOverallMin":myOverallMin})
            dictValues.update({"myOverallMax":myOverallMax})
            dictValues.update({"myOverallAvgMax":myOverallAvgMax})
            dictValues.update({"myOverallAvgMin":myOverallAvgMin})
            dictValues.update({"myOverallMean":myOverallMean})
            dictValues.update({"binned_means":binned_means})
            dictValues.update({"binned_maxs":binned_maxs})
            dictValues.update({"binned_mins":binned_mins})
            dictValues.update({"binned_avg_maxs":binned_avg_maxs})
            dictValues.update({"binned_avg_mins":binned_avg_mins})
            dictValues.update({"binned_stds":binned_stds})
            dictValues.update({"count_arr":count_arr})



            plt.figure(figsize=(30, 20),dpi=300)
            plt.rc('xtick', labelsize=20)    # fontsize of the tick labels
            plt.rc('ytick', labelsize=20)    # fontsize of the tick labels
            plt.rc('axes',labelsize=30)


            myplot = sns.boxplot(
                x="binned",
                y=metric,
                data=df,
                showmeans=True,
                meanline=True,
                meanprops={
                    'color': mean_color,
                    'ls': '-',
                    'lw': 4
                },
            )
            myplot.axhline(df[metric].mean(), color='purple', lw=2, ls='--', zorder=10)


            if metric == "total_waiting_time":
                plt.plot([], [],
                        '--',
                        linewidth=3,
                        color='purple',
                        label=f"\nOverall Mean:          \n{myOverallMean:15,.6f}")
                plt.plot([], [], '-', linewidth=3, color='cyan', label='Binned Mean')
                plt.legend(loc="lower right", bbox_to_anchor=(1.18, .05),fontsize=20)
                plt.ylabel("Waiting Time (seconds)")


            if metric == "pp_slowdown":
                plt.plot([], [],
                        '--',
                        linewidth=3,
                        color='purple',
                        label=f"\nOverall Mean:          \n{myOverallMean:15,.6f}")
                plt.plot([], [], '-', linewidth=3, color='cyan', label='Binned Mean')
                plt.legend(loc="lower right", bbox_to_anchor=(1.18, .05),fontsize=20)
                plt.ylabel("Per Processor Slowdown")

            plt.title(f"Time: {row['time']} Subdivisions: {row['subdivisions']} Unit: {row['subdivisions-unit']}, 2018 January-Nov",\
                    fontdict={"fontsize":20})
            plt.ylim(0,cutOutliers)
            overall_data_xy =(0,1.1)
            overall_data_xycoords="axes fraction"
            overall_data_fontsize=10
            overall_data_fontfamily="monospace"
            overall_data_textcoords="offset pixels"
            fontweights=[700]

            myAnnotate(myplot,dictValues)
            plt.tight_layout()

            if cutOutliersTF:
                filename = output_folder+"/"+metric+"/graphs/"+f"cut_t_{row['time']}_subD_{row['subdivisions']}_subU_{row['subdivisions-unit']}.png"
                plt.savefig(filename, facecolor=(1.0,1.0,1.0),dpi=300)
            else:
                filename = output_folder +"/"+metric+"/graphs/"+f"t_{row['time']}_subD_{row['subdivisions']}_subU_{row['subdivisions-unit']}.png"
                plt.savefig(filename, facecolor=(1.0,1.0,1.0),dpi=300)
            plt.close()

    metric = "total_waiting_time"
    import os
    os.makedirs(output_folder+"/"+metric,exist_ok=True)
    os.makedirs(output_folder+"/"+metric+"/graphs",exist_ok=True)
    if graph_option == "--all":
        plotMyGraphs(cutOutliersTF=True,runs=[1,47])
        plotMyGraphs(cutOutliersTF=False,runs=[1,47],data_also=True)
    elif graph_option == "--outliers":
        plotMyGraphs(cutOutliersTF=False,runs=[1,47],data_also=True)
    elif graph_option == "--non-outliers":
        plotMyGraphs(cutOutliersTF=True,runs=[1,47],data_also=True)
    elif graph_option == "--comparisons":
        plotMyGraphs(cutOutliersTF=True,runs=[1,47],data_only=True)



    metric="total_waiting_time"
    database["binned-means"]=all_binned_means
    database["binned-maxs"]=all_binned_maxs
    database["binned-stds"]=all_binned_stds
    database["binned-avg-maxs"]=all_binned_avg_maxs
    database["binned-avg-mins"]=all_binned_avg_mins
    database["overall-mean"]=all_overall_mean
    database["overall_max"]=all_overall_max
    database["overall-min"]=all_overall_min
    database["overall-avg-max"]=all_overall_avg_max
    database["overall-avg-min"]=all_overall_avg_min
    database["overall-std"]=all_overall_std

    metric = "total_waiting_time"
    rootfolder= output_folder+"/"+metric+"/comparisons/comparisons_overall"
    os.makedirs(rootfolder,exist_ok=True)
    colors = ["green","blue","purple","gold"]
    plt.figure(figsize=(10,10))
    def sortList(myList):
        myList1 = [i for i in myList if not i.find("days")==-1]
        print(myList1)
        myList2 = [i for i in myList if i.find("days")==-1]
        print(myList2)
        myList1.sort(reverse=True)
        myList2.sort()
        return myList2+myList1
    markers=["o","v","^","x","P"]
    for i in database.time.unique():
        df = database.loc[database.time == i]
        count=0
        plt.title(f"Normalized Queue Waiting Time vs Subdivisions",fontdict={"fontsize":18})
        plt.xlabel("Subdivisions (SD)",fontsize=16)
        plt.ylabel("Normalized Queue Waiting Time",fontsize=16)
        myList = df["subdivisions-unit"].unique()
        myList = sortList(myList)
        offsets=((-10,-10),(-10,10),(10,-10),(10,10))
        plt.yticks(ticks=[tick for tick in np.arange(93,102+.5,.5)],labels=[f"{tick}%" for tick in np.arange(93,102+.5,.5)])
        plt.ylim(93.5,102)
        count=0
        for j in myList:
            df2 = df.loc[(df["subdivisions-unit"] == j) | (df.subdivisions == '1')]
            df2 = df2.sort_values(by="subdivisions")
            x=list(df2["subdivisions"])
            y=list(df2["overall-mean"])
            yperc = [(k/y[0])*100 for k in y]
            if j == "1months 00:00:00":
                mylabel="WD = 1 month"
            if j == "8days 00:00:00":
                mylabel="WD = 8 days"
            if j == "4days 00:00:00":
                mylabel="WD = 4 days"
            if j == "2days 00:00:00":
                mylabel="WD = 2 days"
            print(yperc)
            plt.plot(x,yperc,color=colors[count],label=mylabel,marker=markers[count+1])
            #count2=0
            #for k in yperc:
            #    plt.annotate(yperc[count2],xy=(x[count2],y[count2]),xytext=offsets[count],textcoords="offset pixels",fontsize=8,color=colors[count])
            #    count2+=1

            plt.legend()
            count+=1

        plt.tight_layout()
        plt.savefig(f"{rootfolder}/overall_t_{i}.png",dpi=300,facecolor=(1.0,1.0,1.0))
        plt.figure(figsize=(10,10))
        plt.close()

    metric = "total_waiting_time"
    rootfolder=output_folder+"/"+metric+"/comparisons/"
    blues = ["aqua","deepskyblue","steelblue"]
    greens = ["mediumspringgreen","mediumseagreen","green"]
    reds=["lightcoral","indianred","maroon"]
    purples=["rebeccapurple","magenta"]
    colors = blues+greens+reds+purples
    plt.figure(figsize=(10,10))
    def sortList(myList):
        myList1 = [i for i in myList if not i.find("days")==-1]
        print(myList1)
        myList2 = [i for i in myList if i.find("days")==-1]
        print(myList2)
        myList1.sort(reverse=True)
        myList2.sort()
        return myList2+myList1
    count2=0
    for i in database["subdivisions-unit"].unique():
        if i == "1months 00:00:00":
            mylabel="1 month"
        if i == "8days 00:00:00":
            mylabel="8 days"
        if i == "4days 00:00:00":
            mylabel="4 days"
        if i == "2days 00:00:00":
            mylabel="2 days"
        foldername = i.split(" 00:00:00")[0]
        os.makedirs(f"{rootfolder}{foldername}",exist_ok=True)
        df = database.loc[(database["subdivisions-unit"] == i)| (database.subdivisions == '1') ]
        markers=["o","v","^","<",">","s","P","*","x","D","|"]
        for k in df["time"].unique():
            plt.xlabel("Subdivisions (SD)",fontsize=16)
            plt.ylabel("Normalized Queue Waiting Time",fontsize=16)
            df2 = df.loc[df.time == k]
            df2 = df2.sort_values(by="subdivisions")
            plt.title(f"Normalized Queue Waiting Time vs Subdivisions, WD = {mylabel}",fontdict={"fontsize":18})
            plt.yticks(ticks=[tick for tick in np.arange(83.5,106,1.5)],labels=[f"{tick}%" for tick in np.arange(83.5,106,1.5)])
            count=0
            offsets=((-10,-15),(-10,15),(10,-15),(10,15),(-10,-15),(-10,15),(10,-15),(10,15),(-10,-15),(-10,15),(10,-15),(10,15))
            for j in range(0,11,1):
                means = [aMean[j] for aMean in df2["binned-means"]]
                x=list(df2["subdivisions"])
                y=means
                aBin = f"({bins[j]},{bins[j+1]}]"
                yperc = [(z/y[0])*100 for z in y]
                plt.plot(x,yperc,color=colors[count],label=aBin,marker=markers[j])

                count2=0
                #for z in yperc:
                #    plt.annotate(yperc[count2],xy=(x[count2],y[count2]),xytext=offsets[count],textcoords="offset pixels",fontsize=8,color=colors[count])
                #    count2+=1
                count+=1
            plt.legend(loc="lower left")
            plt.tight_layout()
            plt.rc('xtick', labelsize=12)
            plt.rc('ytick',labelsize=12)
            plt.axhline(y=100,xmax=8,linestyle="dashed",color="red")
            plt.savefig(f"{rootfolder}{foldername}/compare_t_{k}.png",dpi=300,facecolor=(1.0,1.0,1.0))
            plt.close()
            plt.figure(figsize=(10,10))
        count2+=1

