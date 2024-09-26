#!/usr/bin/env python3
"""
Usage:
    aggregate_aggregates.py (-i <PATH> | -f <PATH>) [--batches <int>] [ --output <PATH>][ --comparison-skip <STR>]

Required Options:
    -i <PATH> --input <PATH>    The folder and base filename
                                ex: /path/to/files/some_experiment
                                    when files are:
                                    /path/to/files/some_experiment_b1.csv
                                    /path/to/files/some_experiment_b2.csv
    -f <PATH> --folder <PATH>   The folder base name with total_makespan.csv inside
                                ex: /path/to/folder
                                    when folders containing total_makespan.csv are:
                                    /path/to/folder_b1
                                    /path/to/folder_b2
Options:
    --comparison-skip <STR>     skip columns that may be missing.
                                format: "column1,column2,column3"
    -o FOLDER --output FOLDER   where the output should go
                                [default: <input>_agg.csv]
    -b <int>  --batches <int>   how many batches to concatenate.
                                If ommited or -1, will concatenate all files matching the base filename.
                                [default: -1]

"""


from docopt import docopt, DocoptExit
import pandas as pd
import os
import sys
import re
from datetime import datetime,timedelta
try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)
def isPartOfBasename(aFile,basename,folder):
    if folder == False:
        regEX = re.compile(f"^{basename}[_]b[0-9]+[.]csv$")
    else:
        regEX = re.compile(f"^{basename}[_]b[0-9]+$")
    if regEX.match(aFile):
        return True
    else:
        return False
def rowsEqualThenConcat(row,rowc,ourAddColumns):
    for column in columns_to_compare:
        if row[column] != rowc[column]:
            return False
    #ok they are equal, concat
    #first get total makespans

    tot_row = row["number_of_makespans"]
    tot_rowc =rowc["number_of_makespans"]
    number_of_makespans = tot_row + tot_rowc
    #now combine the columns:
    for column in ourAddColumns:
        if column.count("dhms") == 0:
            print(column)
            row[column] = ((row[column]*tot_row) + (rowc[column] * tot_rowc)) / number_of_makespans
        else:
            thisColumn = column[:-5]
            if not(thisColumn in ourAddColumns):
                thisColumn = thisColumn+"_sec"
            row[column] = str(timedelta(seconds=row[thisColumn]))

    row["number_of_makespans"] = number_of_makespans
    return row
path = args["--input"]
folder = False
if args["--folder"]:
    path = args["--folder"]
    folder=True
skipColumns = [i for i in args["--comparison-skip"].split(",")] if args["--comparison-skip"] else False
directory = os.path.dirname(path)
basename = os.path.basename(path)
batches = int(args["--batches"]) if args["--batches"] != -1 else False
output = args["--output"] if args["--output"] != "<input>_agg.csv" else f"{basename}_agg.csv"


#columns_to_ignore_for_comparison= ["makespan_sec","avg-avg-pp-slowdown","avg-pp-slowdown-tau","avg_tat","avg_avg_utilization","avg_avg_waiting","avg_avg_waiting_dhms","makespan_dhms","avg_tat_dhms","avg-avg-pp-slowdown_dhms","AAE","SMTBF_failures","MTBF_failures","Fixed_failures","number_of_makespans,rejected_not_enough_available_resources,checkpointed_num,percent_checkpointed,checkpointing_on_num,checkpointing_on_percent,id,job,exp]
columns_to_compare = ["nodes","SMTBF","NMTBF","MTTR","fixed-failures","submission_compression","repair-time","exp"]
if skipColumns != False:
    for column in skipColumns:
        columns_to_compare.remove(column)
non_concat_columns = columns_to_compare + ["id","job","number_of_makespans"]

if not batches:
    #ok we need to get a list of all files that have the basename
    if folder == False:
        files = [ aFile for aFile in os.listdir(directory) if (os.path.isfile(aFile) and isPartOfBasename(aFile,basename,folder))]
    else:
        files = [ f"{aFolder}/total_makespan.csv" for aFolder in os.listdir(directory) if (os.path.isdir(aFolder) and isPartOfBasename(aFolder,basename,folder))]
else:
    if folder == False:
        files = [ f"{basename}_b{i}.csv" for i in range(1,batches+1,1)]
    else:
        files = [ f"{basename}_b{i}/total_makespan.csv" for i in range(1,batches+1,1)]
df_fin=pd.DataFrame()
for file in files:
    found = False
    #ok we have the list of files we are going to concatenate, lets start concatenating
    #start by importing the csv files
    print(f"{directory}/{file}")
    df = pd.read_csv(f"{directory}/{file}",sep=",",header=0)
    #now if df_fin is empty just add the df to the the finished
    if df_fin.empty:
        df_fin = pd.concat([df_fin,df],axis=0)
        concat_columns = list(df_fin.columns)
        for column in non_concat_columns:
            concat_columns.remove(column)
    else:
        #ok df_fin is not empty, lets concatenate df with df_fin, row by row (slow)
        for index, row in df_fin.iterrows():
            for indexc,rowc in df.iterrows():
                newRow = rowsEqualThenConcat(row,rowc,concat_columns)
                if type(newRow) != bool:
                    found = True
                    break
            if found:
                df_fin.loc[index]=newRow

#ok we are done, lets output
if "Unnamed: 0" in df_fin.columns:
    df_fin = df_fin.drop(["Unnamed: 0"],axis=1)
df_fin.to_csv(output,sep=",",header=True)
