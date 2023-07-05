"""
Usage:
    get_utilization.py --time STR --file PATH  --nodes INT

Required Options:
    --time STR            the time string in the format:
                            definition of HH:MM:SS*     is two digits for hours followed by a colon,
                                                        followed by two digits for minutes followed by a colon,
                                                        and two digits for seconds followed by more digits for seconds if needed
                            :                                   all data
                            Xd HH:MM:SS* :                      from Xd HH:MM:SS* to end
                            : Xd HH:MM:SS*                      from start until Xd HH:MM:SS*
                            Xd HH:MM:SS* : Yd HH:MM:SS*         from Xd HH:MM:SS*   till   Yd HH:MM:SS*
                            Ex:
                                8d 05:30:20 :                   from 8 days 5 hours, 30 minutes and 20 seconds till the end
                                0d 00:00:25000 :                from 25,000 seconds till the end
                                0d 00:00:25000 : 10d 00:00:00   from 25,000 seconds till 10 days ie 10*24*3600 seconds
                            
    --file PATH            the path to the out_jobs.csv [ must include the name of the csv file, the full path ]

    --nodes INT            The amount of nodes the cluster has
                           [default: 1490]
Options
    --help                 print this usage information
""" 
import pandas as pd  
import sys     
from docopt import docopt,DocoptExit
def get_seconds(days,h,m,s):
    day_secs=int(days)*24*3600
    h_secs = int(h)*3600
    m_secs = int(m)*60
    secs = int(s) + m_secs + h_secs + day_secs
    return secs

def parseTimeString(aTimeStr):
    import numpy as np
    import pandas as pd
    import re
   
    hms="([0-9][0-9]):([0-9][0-9]):([0-9][0-9][0-9]*)"
    or_1="((^[ ]*):([ ]*$))"
    or_2="[ ]*([0-9]*)d[ ]{hms}[ ]*:[ ]*$".format(hms=hms)
    or_3="^[ ]*:[ ]*([0-9]*)d[ ]{hms}[ ]*$".format(hms=hms)
    or_4="^[ ]*([0-9]*)d[ ]{hms}[ ]*:[ ]*([0-9]*)d[ ]{hms}[ ]*$".format(hms=hms)
    regStr="{}|{}|{}|{}".format(or_1,or_2,or_3,or_4)
    regEx=re.compile(regStr)
    match=regEx.match(aTimeStr)
    
    
    if not match == None:
        match = match.groups()
    else:
        print("Error with time string in get_utilization.py")
    if not match[0] == None:
        return -1,-1
    if not match[3] == None:
        start=get_seconds(match[3],match[4],match[5],match[6])
        end = -1
        return start,end
    if not match[7] == None:
        start=-1
        end=get_seconds(match[7],match[8],match[9],match[10])
        return start,end
    if not match[11] == None:
        start=get_seconds(match[11],match[12],match[13],match[14])
        end=get_seconds(match[15],match[16],match[17],match[18])
        return start,end
def get_utilization_from_df(df,timeString,nodes):
    start,end = parseTimeString(timeString)
    if start == -1:
        start = df.starting_time.min()
    if end == -1:
        end = df.finish_time.max()

    df = df.loc[df.finish_time > start]
    df = df.loc[df.starting_time < end]

    df_end_before= df.loc[(df.finish_time < end) & (df.starting_time <=start)]
    df_start_after = df.loc[(df.starting_time > start)&(df.finish_time >= end)]
    df_start_end_inside = df.loc[(df.starting_time > start) & (df.finish_time < end)]
    df_start_end_outside = df.loc[(df.starting_time <= start)&(df.finish_time >= end)]
    util = 0
    if not df_end_before.empty:
        util+=(df_end_before.requested_number_of_resources *(df_end_before.finish_time - start)).sum()
    if not df_start_after.empty:
        util+=(df_start_after.requested_number_of_resources *(end - df_start_after.starting_time)).sum()
    if not df_start_end_inside.empty:
        util+=(df_start_end_inside.requested_number_of_resources*(df_start_end_inside.finish_time - df_start_end_inside.starting_time)).sum()
    if not df_start_end_outside.empty:
        util+=(df_start_end_outside.requested_number_of_resources*(end-start)).sum()
    return (util/(nodes*(end-start)))
if __name__ == '__main__':   
    try:
        args=docopt(__doc__,help=True,options_first=False)
    except DocoptExit:
        print(__doc__)
        sys.exit(1)



    filePath=args["--file"]
    timeString=args["--time"]
    nodes = int(args["--nodes"])
    df = pd.read_csv(filePath,sep=",",header=0)
    util = get_utilization_from_df(df,timeString,nodes)


    print(util)


