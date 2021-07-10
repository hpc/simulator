"""
Usage: 
    post-processing.py -i PATH [-o PATH] [--raw INT] 
    post-processing.py -i PATH [-o PATH] [--raw INT] [--checkpointing-on] [--makespan]
    post-processing.py -i PATH [-o PATH] [--raw INT] --checkpointing-on -a PATH [--makespan]

Arguments:
    FILE                            an absolute location to a file
    PATH                            an absolute location to a directory
    INT                             an integer
    FLOAT                           a decimal number
    
Required Options:
    -i PATH --input=PATH            where out_jobs.csv lives
                       
Options:
    -o PATH --output=PATH           where output lives
                                    [default: input_path]
    --raw INT                       whether to output raw post processing data
                                    raw = 1,debug=2, raw and debug=3
    --makespan                      output makespan at input_path/makespan.csv
                                    outputs avgerage turnaround time, as well as
                                    nodes,SMTBF,NMTBF,AAE,num_checkpointed,
                                    percent_checkpointed
                                    
Checkpointing Options:
  
  --checkpointing-on                process checkpointed data
  -a PATH --avgAE_path=PATH         Path to where avgAE.csv lives
  
"""





import pandas as pd
import numpy as np
import json
from docopt import docopt
import sys
import os

args=docopt(__doc__,help=True,options_first=False)
        



#example conditional required non_int.add_argument('--lport', required='--prox' in sys.argv, type=int)

args["--output"] = args["--output"] if not (args["--output"] == "input_path") else args["--input"]
#path to results of the simulation
path=args["--input"].rstrip('/') + "/out_jobs.csv"

#path to outfile
outfile = args["--output"].rstrip('/') +"/post_out_jobs.csv"
raw_outfile = args["--output"].rstrip('/') +"/raw_post_out_jobs.csv"
raw_outfile_debug = args["--output"].rstrip('/') +"/DEBUG_raw_post_out_jobs.csv"

#CHECKPOINTING
checkpointing = True if args["--checkpointing-on"] else False

raw = int(args["--raw"]) if args["--raw"] else False


if checkpointing:
    if args["--avgAE_path"]:
            avgAE_path=args["--avgAE_path"].rstrip('/') + "/avgAE.csv"
    else:
        avgAE_path=args["--input"].rstrip('/') + "/avgAE.csv"
makespan = True if args["--makespan"] else False


df = pd.read_csv(path,sep=',',header=0,dtype={"job_id": str, "profile": str,"metadata":str,"batsim_metadata":str})
MTBF = df["MTBF"].iloc[0] if not df["MTBF"].isnull().iloc[0] else -1
SMTBF = df["SMTBF"].iloc[0] if not df["SMTBF"].isnull().iloc[0] else -1
error = df["Tc_Error"].iloc[0]


df["submission_time"]=df["submission_time"].astype(np.double)
df["starting_time"]=df["starting_time"].astype(np.double)
df["execution_time"]=df["execution_time"].astype(np.double)
df["finish_time"]=df["finish_time"].astype(np.double)
df["waiting_time"]=df["waiting_time"].astype(np.double)
df["turnaround_time"]=df["turnaround_time"].astype(np.double)
df["stretch"]=np.round(df["stretch"])
df["job_id"] = df.job_id.astype('str')

if set(['metadata','batsim_metadata']).issubset(df.columns):
    #select just jod_id and metadata columns
    metadf = df[['job_id','metadata']]
    batsim_metadf = df[['job_id','batsim_metadata']]
    #select just the rows where metadata is not null
    metadf = metadf[~metadf["metadata"].isnull()]
    batsim_metadf = batsim_metadf[~batsim_metadf['batsim_metadata'].isnull()]
    
    # function to apply to all metadata strings...turns them into dict[ionaires]
    def string_to_dict(dict_string):
        # Convert to proper json format
        dict_string = dict_string.replace("'", '"')
        return json.loads(dict_string)

    #apply the function to all metadata strings
    metadf.metadata = metadf.metadata.apply(string_to_dict)
    batsim_metadf.batsim_metadata = batsim_metadf.batsim_metadata.apply(string_to_dict)
    #make a dataframe out of the metadata dict (metadata must not be nested)
    onlymeta = pd.DataFrame(list(metadf['metadata']))
    if 'work_progress' in onlymeta:
        onlymeta['previous_work_progress'] = onlymeta['work_progress']
        onlymeta = onlymeta.drop(['work_progress'],axis=1)
    only_batsim_metadata = pd.DataFrame(list(batsim_metadf['batsim_metadata']))
    #sync up onlymeta and the metadf indices
    onlymeta.index=metadf.index
    only_batsim_metadata.index = batsim_metadf.index
    #concatenate df and onlymeta
    df=pd.concat([df,onlymeta],axis=1,sort=False)
    df=pd.concat([df,only_batsim_metadata],axis=1,sort=False)
    if 'checkpointed' in df:
        df.loc[df['checkpointed'].isnull(),'checkpointed']="False"
    else:
        df['checkpointed'] = "False"
#first just assume all jobs have themselves as parents
df['parent']=df['job_id']
#get the jobs that have a pound sign indicating they were resubmitted
resubmits=df[df.job_id.str.contains("#", regex=False)]

#extract the job_id into their parent and resubmit number parts
#this forms a dataframe with the two columns parent and resubmit
#this includes an edit allowing for a underscore(_) before the (#).  The underscore
#is used in grizzly workload creator to signify the index in the workload so as to
#form a unique jobid when randomly choosing the same job.
resubmits_ext=resubmits.job_id.str.extract(r'(?P<parent>\d+[_]?\d*)#(?P<resubmit>\d+)')

#now we can just update the 'parent' column.  If it
#wasn't a resubmit it is just left as its job_id from above
df.update(resubmits_ext.parent)

#now we add the column resubmits to the finished product,this is the
#resubmit number and not the amount of times it was resubmited
# i.e. the number after the pound sign
df['resubmit']=resubmits_ext['resubmit']

# copy df and sum up all the execution_times grouped by the parent
# so if 5 jobs had parent "3", those 5 jobs' execution_times are summed
# and stored in 'total_execution_time'. ditto on waiting time. real
# finish time is the max finish time in the group. num_resubmits is the count - 1
# in the group. real_final_state is the last resubmit's final state.
df2=df

df2['total_execution_time'] = df.groupby('parent')['execution_time'].transform('sum')
df2['total_waiting_time'] = df.groupby('parent')['waiting_time'].transform('sum')
df2['real_finish_time'] = df.groupby('parent')['finish_time'].transform('max')
df2['num_resubmits']=df2.groupby('parent')['job_id'].transform('count') - 1
df2['total_turnaround_time']=df2.groupby('parent')['turnaround_time'].transform('sum')
df2=df2.sort_values(by=['parent','job_id'],axis=0)
if raw==1 or raw==3:
    df2.to_csv(raw_outfile)

#first get all the resubmits and make sure we are getting a copy and not a view
df2Resubmits = df2[~df2["resubmit"].isnull()].copy(deep=True)
#Now get nonresubmits including the parents of resubmits
df2NonResubmits = df2[df2["resubmit"].isnull()]
#Now get all the unique parents from the resubmits
df2ResubmitParents = df2Resubmits.parent.unique()
#Next filter out the Parents from the Non Resubmits
df2Parents = df2NonResubmits[df2NonResubmits["parent"].isin(df2ResubmitParents)]
#Next save the NonResubmits minus the parents of resubmits
df2NonResubmits = df2NonResubmits[~df2NonResubmits["parent"].isin(df2ResubmitParents)].copy(deep=True)
# need all resubmits to be int so we can get max.  NaN was giving a problem
# so we just set it to 0 here.(may not be needed anymore)
df2Parents.loc[df2Parents.resubmit.isnull(),'resubmit'] = 0
df2Parents.resubmit = df2Parents.resubmit.astype('int')
df2Resubmits.resubmit = df2Resubmits.resubmit.astype('int')
df2NonResubmits["resubmit"] = 0
#if we are checkpointing do the following
if checkpointing:
    #for all the resubmits set the maxresubmit(could've just used num_resubmits but want to make it clear
    #for the future)
    df2Resubmits['maxresubmit'] = df2Resubmits.groupby('parent')['resubmit'].transform('max').copy(deep=True)
    #now save the rows where it is the max resubmit.  Now we can set the parent's information
    #to some of that of the max resubmit  (for instance final_state,work_progress,total_dumps)
    df2MaxResubmits = df2Resubmits.loc[df2Resubmits['maxresubmit']==df2Resubmits['resubmit']].copy(deep=True)
    
    df2MaxResubmits["real_final_state"]=df2MaxResubmits["final_state"]
    #make the column real_final_state in the Parents.  They will be replaced
    df2Parents["real_final_state"]=np.nan
    #sort max resubmits and parents so that they are at the same index
    df2MaxResubmits=df2MaxResubmits.sort_values(by=['parent','job_id'])
    df2Parents=df2Parents.sort_values(by=['parent','job_id'])
    #set the actual numbers of the index of max resubmits equal to parents index
    print(len(df2Parents))
    df2MaxResubmits.index = df2Parents.index
    #set the columns we want to replace (update) from max resubmits to parents
    if set(['num_dumps','previous_work_progress']).issubset(df2MaxResubmits.columns):
        cols = ['metadata','batsim_metadata','checkpointed','num_dumps','previous_work_progress',\
               'dumps','work','total_dumps','work_progress','real_final_state']
    else:
        cols = ['metadata','batsim_metadata','checkpointed',\
               'dumps','work','total_dumps','work_progress','real_final_state']
    #keep the columns we want to update
    df2MaxResubmits=df2MaxResubmits[cols]
    #update
    df2Parents.update(df2MaxResubmits)
    #NonResubmits need a real_final_state as well.
    df2NonResubmits['real_final_state']=df2NonResubmits['final_state']
else:
    df2Resubmits['maxresubmit'] = df2Resubmits.groupby('parent')['resubmit'].transform('max').copy(deep=True)
    #now save the rows where it is the max resubmit.  Now we can set the parent's information
    #to some of that of the max resubmit  (for instance final_state)
    df2MaxResubmits = df2Resubmits.loc[df2Resubmits['maxresubmit']==df2Resubmits['resubmit']].copy(deep=True)
    
    df2MaxResubmits["real_final_state"]=df2MaxResubmits["final_state"]
    #make the column real_final_state in the Parents.  They will be replaced
    df2Parents["real_final_state"]=np.nan
    #sort max resubmits and parents so that they are at the same index
    df2MaxResubmits=df2MaxResubmits.sort_values(by=['parent','job_id'])
    df2Parents=df2Parents.sort_values(by=['parent','job_id'])
    #set the actual numbers of the index of max resubmits equal to parents index
    df2MaxResubmits.index = df2Parents.index
    #set the columns we want to replace (update) from max resubmits to parents
    cols = ['metadata','batsim_metadata','real_final_state']
    #keep the columns we want to update
    df2MaxResubmits=df2MaxResubmits[cols]
    #update
    df2Parents.update(df2MaxResubmits)
    #NonResubmits need a real_final_state as well.
    df2NonResubmits['real_final_state']=df2NonResubmits['final_state']
    
df2 = pd.concat([df2Resubmits,df2Parents,df2NonResubmits],axis=0,sort=False)
df2=df2.sort_values(by=['parent','job_id'],axis=0)
if raw==2 or raw==3:
    df2.to_csv(raw_outfile_debug)

#df3 becomes everything df2 was without the resubmitted jobs
df3=df2[df2.resubmit==0]

#reorder columns
if checkpointing:
    cols = ['job_id','workload_name','workload_num_machines','profile','submission_time','requested_number_of_resources',\
            'requested_time','success','real_final_state','starting_time','total_execution_time',\
            'num_resubmits','real_finish_time','checkpointed','total_waiting_time','total_turnaround_time','total_dumps','work_progress',\
            'checkpoint_time','dump_time','read_time','delay','real_delay','MTBF','SMTBF','Tc_Error']
else:
    cols = ['job_id','workload_name','workload_num_machines','profile','submission_time','requested_number_of_resources'\
            ,'requested_time','success','real_final_state','starting_time','total_execution_time'\
            ,'real_finish_time','total_waiting_time','total_turnaround_time','delay','MTBF','SMTBF','Tc_Error']
df3=df3[cols]
if checkpointing:
    df3.loc[~(df3['delay'] == df3['real_delay']),'checkpointing_on']=True
    df3.loc[df3['delay']==df3['real_delay'],'checkpointing_on']=False

avgAE = 0
if checkpointing:
    df3['application_efficiency']=df3['real_delay']/df3['total_execution_time']
    avgAE = (df3['real_delay']*df3['requested_number_of_resources']).sum() \
        /(df3['total_execution_time']*df3['requested_number_of_resources']).sum()
else:
    df3['application_efficiency']=df3['delay']/df3['total_execution_time']
    avgAE = (df3['delay']*df3['requested_number_of_resources']).sum() \
        /(df3['total_execution_time']*df3['requested_number_of_resources']).sum()
        
print("Average App Efficiency: ",avgAE)
df3['Average App Efficiency'] = avgAE



avg_tat = df3['total_turnaround_time'].mean()
if makespan and checkpointing: 
    makespan = df3.real_finish_time.max() - df3.starting_time.min()
    checkpointed_num = len(df3.loc[df3.checkpointed == True])
    checkpointing_on_num = len(df3.loc[df3.checkpointing_on == True])
    percent_checkpointed = float(checkpointed_num/float(len(df3)))
    checkpointing_on_percent = float(checkpointing_on_num/float(len(df3)))
    outputMakespan = args["--input"].rstrip("/") + "/makespan.csv"
    from datetime import datetime, timedelta
    sec = timedelta(seconds=(int(makespan)))
    sec2=timedelta(seconds=(int(avg_tat)))
    avg_tat_dhms =str(sec2)
    makespan_dhms = str(sec)
    numNodes = df3["workload_num_machines"].values[0]
    
    makespan_df = pd.DataFrame({"nodes":numNodes,
                                "SMTBF":[SMTBF],
                                "NMTBF":[np.round(SMTBF*numNodes)],
                                "makespan_sec":[makespan],
                                "makespan_dhms":[makespan_dhms],
                                "AAE":[avgAE],
                                "checkpointed_num":[checkpointed_num],
                                "percent_checkpointed":[percent_checkpointed],
                                "avg_tat":[avg_tat],
                                "avg_tat_dhms":[avg_tat_dhms],
                                "checkpointing_on_num":[checkpointing_on_num],
                                "checkpointing_on_percent":[checkpointing_on_percent],
                                "number_of_jobs":[len(df3)]
                               })
    makespan_df.to_csv(outputMakespan,mode='w',header=True)
elif makespan:
    makespan = df3.real_finish_time.max() - df3.starting_time.min()
    
    outputMakespan = args["--input"].rstrip("/") + "/makespan.csv"
    from datetime import datetime, timedelta
    sec = timedelta(seconds=(int(makespan)))
    sec2=timedelta(seconds=(int(avg_tat)))
    avg_tat_dhms =str(sec2)
    makespan_dhms = str(sec)
    numNodes = df3["workload_num_machines"].values[0]
    
    makespan_df = pd.DataFrame({"nodes":numNodes,
                                "SMTBF":[SMTBF],
                                "NMTBF":[np.round(SMTBF*numNodes)],
                                "makespan_sec":[makespan],
                                "makespan_dhms":[makespan_dhms],
                                "AAE":[avgAE],
                                "avg_tat":[avg_tat],
                                "avg_tat_dhms":[avg_tat_dhms],
                                "number_of_jobs":[len(df3)]
                                
                               })
    makespan_df.to_csv(outputMakespan,mode='w',header=True)
df3.to_csv(outfile)

if (not(MTBF == -1)):
    AE_df=pd.DataFrame({'x':[error],
                  'y':[avgAE],
                  'MTBF':[MTBF]})
    AE_df.to_csv(avgAE_path,mode='w',header=True)
elif (not(SMTBF == -1)):
    AE_df=pd.DataFrame({'x':[error],
                        'y':[avgAE],
                        'SMTBF':[SMTBF]})
    AE_df.to_csv(avgAE_path,mode='w',header = True)
    
