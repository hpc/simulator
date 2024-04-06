"""
Usage:
    generate_config.py --config-info <type>
    generate_config.py -i FILE -o PATH [--basefiles PATH] [--output-config] [--increase-heldback-nodes] [options]

Required Options 1:
    --config-info <type>                    Display how the json config is supposed to look like
                                            as well as how each part of it can look like.
                                            <type> can be:
                                                general | sweeps |
                                                node-sweep | SMTBF-sweep | checkpoint-sweep | checkpointError-sweep | performance-sweep |
                                                grizzly-workload | synthetic-workload |
                                                input-options | output
Required Options 2:
    -i <FILE> --input <FILE>                Where our config lives
    -o <PATH> --output <PATH>               Where to start outputting stuff
                                        
Options:
    --basefiles <PATH>                      Where base files go.  Make sure you have a 'workloads' and 'platforms' folder
                                            in this path.
                                            [default: False]

    --output-config                         If this flag is included, will output the input file to --output directory
                                            as --input filename

    --increase-heldback-nodes               If this flag is included, will treat heldback nodes as additional nodes

    --test-suite                            If this flag is included, puts the progress.log file one folder up from --output
                                            Otherwise puts it in --output

Checkpoint Batsim Options:
    --start-from-checkpoint <INT>           Set this if starting from a checkpoint.  The <INT> is the number of the checkpoint.
                                            Typically '1', the latest. -1 means to not to start from a checkpoint...the default.
                                            [default: -1]
    --skip-completed-sims                   Set this if you want to skip starting from a checkpoint if the sim is included in progress.log with success
                                            
    --discard-last-frame                    Used in conjunction with --start-from-checkpoint and can be used with --start-from-frame
                                            Does not make sense to use with --start-from-checkpoint-keep
                                            Will not change any of the kept expe-out_#'s and will not keep the current expe-out

    --start-from-checkpoint-keep <INT>      Used in conjunction with --start-from-checkpoint
                                            Will keep expe-out_1 through exp-out_<INT>.  Only use with --start-from-checkpoint
                                            When starting from checkpoint, the current expe-out folder becomes expe-out_1.
                                            Previous expe-out_1 will become expe-out_2 if keep is set to 2
                                            If you have expe-out_1,expe-out_2,expe-out_3 and keep is 3:
                                                will move expe-out_1 to expe-out_2
                                                will move expe-out_2 to expe-out_3
                                                will delete old expe-out_3
                                            [default: 1]

    --start-from-frame <INT>                Only used with --start-from-checkpoint and in conjunction with --start-from-checkpoint-keep
                                            Will use the expe-out_<INT> folder to look for the checkpoint data
                                                So if you were invoking --start-from-checkpoint-keep 2, you would have
                                                expe-out_1 and expe-out_2,   once you started from a checkpoint twice
                                                If you use --start-from-frame 2 you will be using the checkpoint_[--start-from-checkpoint]
                                                folder located in the expe-out_2 folder ( the expe-out_[--start-from-frame] folder)
                                            Here, '0' is the original expe-out folder that becomes expe-out_1
                                            If --discard-last-frame is used, then default here is 1. 0 is not allowed and will become 1 if used.
                                            [default: 0]
    

"""


from docopt import docopt,DocoptExit
import os
import sys
import json
import numpy as np
import pathlib
import generate_config_strings as cfgStr
from shutil import copy2
from sweeps import *
import sweeps
from copy import deepcopy
import re
import stripJsonComments
import start_from_checkpoint
import functions

#we need these to be global variables
ourInput = dict()
ourOutput = dict()

#simple function to determine if the key is in the dictionary
def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
       
        
#workload names include all the options in its name to distinguish it.  Some options
#have a colon or slash in it.  This replaces those with _CLN_ or _SL_
def nocolon(myString):
    myString=str(myString)
    if not myString.find("/")==-1:
        slashes=len(myString.split("/"))
        if slashes > 1:
            myString = myString.split("/")[slashes-1]
    myString=myString.replace("/","_SL_")
    return myString.replace(":","_CLN_")
    

def parseIds(idString):
    import re
    import sys
    if isinstance(idString,list):
        return idString
    regEx=re.compile(".*(\[[0-9,]+\]).*")
    match=regEx.match(idString)
    #does the idString match a range type of String   ie  [1,3,4]
    if match:
        #yes it does
        return idString.strip("][").split(",")
    else:
        # ok so we don't have a list we have a range  ie  2;10;2     2 to 10(inclusive) by 2's
        aMin,aMax,aStep = idString.split(";")
        if aMin and aMax and aStep:
            aMin=int(aMin)
            aMax=int(aMax)
            aStep=int(aStep)
            return list(range(aMin,aMax+aStep,aStep))
        else:
            print("Error 'workload-ids' is invalid")
            sys.exit(1)

def equaldf(df1,idf2,cols):
    equals = []
    for i in idf2.rows:
        print(i)
        print(type(i))
        equal = True
        for col in cols:
            print(col)
            print(type(col))
            if i[col]!=df1[col]:
                equal = False
        if equal == True:
            equals.append(i.index)
    return equals




###########################################################################################################    
####                                                                                                  #####
####                                 Create a synthetic workload                                      #####
####                                                                                                  #####
###########################################################################################################		

def createSyntheticWorkload(ourId,submission_compression,config,resv,nodes,jobs,experiment,basefiles,exp,base):
    import uuid
    import pandas as pd
    import os
    df = pd.DataFrame()
    homePath = os.environ['HOME']
    
    if basefiles:
        path= basefiles+"/workloads"
        scriptPath=basefiles
    else:
        basefiles = str(os.path.expanduser(os.path.dirname(os.path.abspath(__file__))))
        scriptPath = basefiles
        path = scriptPath+"/workloads"
    db_path=path+"/workloads_db.csv"
    database=pd.DataFrame()
    command="touch {db_path}".format(db_path=db_path)
    os.system(command)
    
    if os.path.isfile(db_path) and os.path.getsize(db_path) > 0:
        print("line 116")
        database=pd.read_csv(db_path,sep="|",header=0,dtype=str)
    else:
        database=pd.DataFrame()
    print(db_path)
    command = ""
    profile_type = config["type"]
    machine_speed = config['machine-speed'] if profile_type == "parallel_homogeneous" else -1
    machine_speed_str = ""
    if not type(machine_speed) == bool:
        machine_speed_str = " --machine-speed "+str(machine_speed)
    type_str = "delay" if profile_type == "delay" else "ph"+ str(machine_speed)
    numberOfJobs=int(config['number-of-jobs']) if dictHasKey(config,'number-of-jobs') else False
    if (numberOfJobs == False) and (not (type(jobs) == bool)):
        numberOfJobs = int(jobs)
    index=ourId
    print(ourId)
    noCheck=config["force-creation"] if dictHasKey(config,"force-creation") else False
    numberOfResources=config['number-of-resources'] if dictHasKey(config,'number-of-resources') else False
    durationTime = config['duration-time'] if dictHasKey(config,'duration-time') else False
    submission=config['submission-time'] if dictHasKey(config,'submission-time') else False
    wallclockLimit = config['wallclock-limit'] if dictHasKey(config,'wallclock-limit') else False
    readtime = config['read-time'] if dictHasKey(config,'read-time') else False
    dumptime = config['dump-time'] if dictHasKey(config,'dump-time') else False
    checkpoint = config['checkpoint-interval'] if dictHasKey(config,'checkpoint-interval') else False
    scaleWidths=int(config['scale-widths-based-on']) if dictHasKey(config,'scale-widths-based-on') else False
    scaleTimeWidth=int(config['scale-time-width-based-on']) if dictHasKey(config,'scale-time-width-based-on') else False
    seed = int(config["seed"]) if dictHasKey(config,"seed") else False
    all_cols=["filename","nodes","number-of-jobs","index","type","machine-speed","seed","number-of-resources","duration-time","submission-time","submission-compression","wallclock-limit","read-time","dump-time","checkpoint-interval","scale-widths-based-on","scale-time-width-based-on","reservation-json"]
    cols=all_cols
    cols_for_folder=["folder","experiment"] + all_cols
    cols_without_filename=all_cols[1:]
    cols_without_scale=cols_without_filename
    cols_without_scale.remove("scale-widths-based-on")
    cols_without_scale.remove("scale-time-width-based-on")
    df["nodes"]=[str(nodes)]
    df["number-of-jobs"]=[str(numberOfJobs)]
    df["index"]=[str(index)]
    df["type"]=[str(profile_type)]
    df["machine-speed"]=[str(machine_speed)]
    df["number-of-resources"]=[str(numberOfResources)]
    df["duration-time"]=[str(durationTime)] 
    df["submission-time"]=[str(submission)]
    df["submission-compression"]=[str(submission_compression)]
    df["wallclock-limit"]=[str(wallclockLimit)]
    df["read-time"]=[str(readtime)]
    df["dump-time"]=[str(dumptime)]
    df["checkpoint-interval"]=[str(checkpoint)]
    df["scale-widths-based-on"]=[str(scaleWidths)]
    df["scale-time-width-based-on"]=[str(scaleTimeWidth)]
    df["reservation-json"]=[str(resv)]
    df["seed"]=[str(seed)]
    
      
    filename = "%d_nodes_%d_jobs_%s.json"%(nodes,numberOfJobs,str(uuid.uuid4()))
    # if we are scaling widths we need a workload to be based on the original "scale-widths-based-on", notice location2 is the same as location
    # except location2 has scaleWidths for nodes
    if not type(scaleWidths) == bool:
        equal = pd.Series()
        if not database.empty:
            df["nodes"]=[str(scaleWidths)]    
            df2 = pd.merge(database,df,how="left",on=cols_without_scale, indicator='Exist')
            df2['Exist'] = np.where(df2.Exist == 'both', True, False)
            equal = df2.loc[df2["Exist"]==True].head(n=1)
            
        
     
        if (len(equal) == 0) or database.empty :
            #ok we need to make a workload to scale
            filename2 = "%d_nodes_%d_jobs_%s.json"%(nodes,numberOfJobs,str(uuid.uuid4()))
            df["filename"]=[filename2]
            if not database.empty:
                database=pd.concat([database,df])
            else:
                database=df
            database=database[cols]
            database.to_csv(db_path,sep="|",header=True,index=False)
            
            # we must make a workload
            command = """python3 {scriptPath}/generate_synthetic_workload.py
                        --db {db_path} --file-name {filename}""".format(scriptPath=scriptPath,db_path=db_path,filename=filename2).replace("\n","")
            
            os.system(command)
    df["nodes"]=[str(nodes)]

    
    equal=pd.Series()
    if not database.empty:
       df2 = pd.merge(database,df,how="left",on=cols_without_filename,indicator='Exist')
       df2['Exist'] = np.where(df2.Exist == 'both', True, False)
       equal = df2.loc[df2["Exist"]==True].head(n=1)
    

    location=""
    folderDF_filename = filename
    filegood=False
    if (len(equal) > 0) and not noCheck:
    #ok supposedly we have a workload file
    #lets make sure
        #print("line 200")
        #mask=(df[cols_without_filename].isin(database[cols_without_filename])).all(axis=1)

        location=os.path.dirname(db_path)+"/"+equal["filename"].values[0]
        if os.path.exists(location):
            filegood=True
            folderDF_filename = equal["filename"].values[0]
    #whether we make a new workload or not, output to folder db
    folderDF = deepcopy(df)
    folderDF["folder"]=[experiment]
    folderDF["experiment"]=[exp]
    folderDF["filename"]=[folderDF_filename]
    folderDF=folderDF[cols_for_folder]
    folderDatabase = pd.DataFrame()
    folderDBPath = base+"/synth_workloads_db.csv"
    command="touch {db_path}".format(db_path=folderDBPath)
    os.system(command)
    if os.path.isfile(folderDBPath) and os.path.getsize(folderDBPath) > 0:
        folderDatabase = pd.read_csv(folderDBPath,header=0,sep="|")
    folderDatabase = pd.concat([folderDatabase,folderDF])
    folderDatabase.to_csv(folderDBPath,header=True,sep="|",index=False)
    if (len(equal) == 0) or database.empty or filegood == False or noCheck == True:
       
        #ok we need to make a workload
        print(f"making synthetic workload: {filename}")
        df["filename"] =[filename]
        if not database.empty:
            database=pd.concat([database,df])
        else:
            database=df
        database=database[cols]
        database.to_csv(db_path,sep="|",header=True,index=False)

        location=os.path.dirname(db_path)+"/"+filename
        # we must make a workload
        command = """python3 {scriptPath}/generate_synthetic_workload.py
                    --db {db_path} --file-name {filename}""".format(scriptPath=scriptPath,db_path=db_path,filename=filename).replace("\n","")
        print("cmd: "+command)
        os.system(command)
        #TODO change workload if only difference is # nodes
        # else: # ok location without the nodes WAS already made, we simply have to modify it for the amount of nodes
        #     for orig,mod in modWorkloads.items():
        #         if modLocation == mod:
                    
        #             if not type(scaleWidths)==bool:
        #                 command = "python3 {scriptPath}/change_workload.py -i {location2} -o {location} --nodes {nodes} --scale-widths-based-on {scaleWidths}".format(
        #                     scriptPath=scriptPath,location2=location2,location=location,nodes=nodes,scaleWidths=scaleWidths)
        #             else:
        #                 command="python3 {scriptPath}/change_workload.py -i {orig} -o {location} --nodes {nodes}".format(
        #                     scriptPath=scriptPath,location=location,orig=orig,nodes=nodes)
        #             break
        #     print(command)
        #     os.system(command)
    return location,profile_type,machine_speed,submission,command

###########################################################################################################    
####                                                                                                  #####
####                    Create a workload based on workload data we already had                       #####
####                                                                                                  #####
###########################################################################################################

##TODO incorporate jobs
def createGrizzlyWorkload(ourId,submission_compression,config,resv,nodes,jobs,experiment,basefiles,exp,base):
    import uuid
    import pandas as pd
    import os

    df = pd.DataFrame()
    homePath = os.environ['HOME']
    command=""
    
    if basefiles:
        path= basefiles+"/workloads"
        scriptPath=basefiles
    else:
        basefiles = str(os.path.expanduser(os.path.dirname(os.path.abspath(__file__))))
        scriptPath = basefiles
        path = scriptPath+"/workloads"
    db_path=path+"/workloads_grizzly_db.csv"
    database=pd.DataFrame()
    command="touch {db_path}".format(db_path=db_path)
    os.system(command)
  
    if os.path.isfile(db_path) and os.path.getsize(db_path) > 0:
      
        database=pd.read_csv(db_path,sep="|",header=0,dtype=str)
    else:
        database=pd.DataFrame()
    index=ourId
    print("ourId %d" % index)
    #TODO profile_type
    profile_type=config["type"]
    
    
    time = config['time']
    inputPath=config['input']
    index = config["index"] if dictHasKey(config,"index") else index
    noCheck=config["force-creation"] if dictHasKey(config,"force-creation") else False
    numberOfJobs=int(config['number-of-jobs']) if dictHasKey(config,'number-of-jobs') else False
    randomSelection = config['random-selection'] if dictHasKey(config,'random-selection') else False
    submissionTime = config["submission-time"] if dictHasKey(config,"submission-time") else False
    wallclockLimit = config['wallclock-limit'] if dictHasKey(config,'wallclock-limit') else False
    submission=config['submission-time'] if dictHasKey(config,'submission-time') else False
    readtime = config['read-time'] if dictHasKey(config,'read-time') else False
    dumptime = config['dump-time'] if dictHasKey(config,'dump-time') else False
    checkpoint = config['checkpoint-interval'] if dictHasKey(config,'checkpoint-interval') else False
    machine_speed = config["machine-speed"] if dictHasKey(config,"machine-speed") else False
    copies=config["copy"] if dictHasKey(config,"copy") else False
    all_cols=["filename","nodes","time","input-path","number-of-jobs","random-selection","index","type","submission-time","submission-compression","machine-speed","wallclock-limit","read-time","dump-time","checkpoint-interval","copy","reservation-json"]
    cols=all_cols
    cols_for_folder=["folder","experiment"] + all_cols
    cols_merge=["filename_x"]+ all_cols
    cols_without_filename=all_cols[1:]
    df["filename"]=[str(False)]
    df["nodes"]=[str(nodes)]
    df["time"]=[str(time)]
    df["input-path"]=[str(inputPath)]
    df["number-of-jobs"]=[str(numberOfJobs)]
    df["random-selection"]=[str(randomSelection)]
    
    df["index"]=[str(index)]
    df["type"]=[str(profile_type)]
    df["submission-time"]=[str(submissionTime)]
    df["submission-compression"]=[str(submission_compression)]
    df["machine-speed"]=[str(machine_speed)]
    df["wallclock-limit"]=[str(wallclockLimit)]
    df["read-time"]=[str(readtime)]
    df["dump-time"]=[str(dumptime)]
    df["checkpoint-interval"]=[str(checkpoint)]
    df["copy"]=[str(copies)]
    df["reservation-json"]=[str(resv)]
        
    filename = "%d_nodes_%s__%s_time_%s.json"%(nodes,time.split(":")[0],time.split(":")[1],str(uuid.uuid4()))
   
    # if we are scaling widths we need a workload to be based on the original "scale-widths-based-on", notice location2 is the same as location
    # except location2 has scaleWidths for nodes
    equal = pd.Series()
    if not database.empty:
        df2 = pd.merge(database,df,how="left",on=cols_without_filename, indicator='Exist')
        df2['Exist'] = np.where(df2.Exist == 'both', True, False)
        equal = df2.loc[df2["Exist"]==True].head(n=1)

    location=""
    filegood=False
    folderDF_filename = filename
    if (len(equal) > 0) and not noCheck:
    #ok supposedly we have a workload file
    #lets make sure
        print("not mask empty and len database[mask]) > 0")
        location=os.path.dirname(db_path)+"/"+equal["filename_x"].values[0]
        if os.path.exists(location):
            filegood=True
            folderDF_filename = equal["filename_x"].values[0]
    #output the df to the database in folder
    folderDF = deepcopy(df)
    folderDF["folder"]=[experiment]
    folderDF["experiment"]=[exp]
    folderDF["filename"]=[folderDF_filename]
    folderDF=folderDF[cols_for_folder]
    folderDatabase = pd.DataFrame()
    folderDBPath = base+"/grizzly_workloads_db.csv"
    command="touch {db_path}".format(db_path=folderDBPath)
    os.system(command)
    if os.path.isfile(folderDBPath) and os.path.getsize(folderDBPath) > 0:
        folderDatabase = pd.read_csv(folderDBPath,header=0,sep="|")
        folderDatabase = pd.concat([folderDatabase,folderDF])
    else:
        folderDatabase = folderDF
    folderDatabase.to_csv(folderDBPath,header=True,sep="|",index=False)
    

    if (len(equal) == 0 or filegood == False or noCheck == True):
        #ok we need to make a workload
        print(f"making 'grizzly' workload: {filename}")
        df["filename"]=[filename]
        if not database.empty:
            database=pd.concat([database,df])
        else:
            database=df
        database=database[cols]
        database.to_csv(db_path,sep="|",header=True,index=False)
        location=os.path.dirname(db_path)+"/"+filename
        # we must make a workload
        command = """python3 {scriptPath}/generate_grizzly_workload.py
                    --db {db_path} --file-name {filename}""".format(scriptPath=scriptPath,db_path=db_path,filename=filename).replace("\n","")

        os.system(command)

    return location,profile_type,machine_speed,submission,command

###########################################################################################################    
####                                                                                                  #####
####                  Create a platform file ( just changing # nodes,cores,speeds )                   #####
####                                                                                                  #####
###########################################################################################################

def createPlatform(nodes,cores,speeds,basefiles):
    
    homePath = os.environ['HOME']
    if basefiles:
        path= basefiles+"/platforms"
        scriptPath=basefiles
    else:
        path = homePath+"/basefiles/platforms"
        scriptPath = homePath + "/basefiles"
    outputPath ="{path}/platform_{nodes}_{cores}_{speeds}.xml".format(path=path,nodes=nodes,cores=cores,speeds=speeds)
    inPath="{path}/platform_1490.xml".format(path=path)
    if not os.path.exists(outputPath):
        command = "python3 {scriptPath}/change_platform.py -i {inPath} -o {outputPath} --nodes {nodes} --cores {cores} --speeds {speeds}".format(
            scriptPath=scriptPath,nodes=nodes,cores=cores,speeds=speeds,outputPath=outputPath,inPath=inPath)
        os.system(command)
    return outputPath













#get our docopt options read in
try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)
###########################################################################################################    
####                                                                                                  #####
####        This whole section is to output information on how to construct a config file             #####
####                                                                                                  #####
###########################################################################################################
if args["--config-info"]:
    configStrings=cfgStr.getStrings()
    if dictHasKey(configStrings,args["--config-info"]):
        print(configStrings[args["--config-info"]])
        sys.exit(0)
    else:
        print(__doc__)
        sys.exit(1)
        
###########################################################################################################    
####                                                                                                  #####
####                      This is the start of the main code                                          #####
####                                                                                                  #####
###########################################################################################################
profile_type=""
base = args["--output"].rstrip('/')
testSuite = True if args["--test-suite"] else False
skipCompletedSims = True if args["--skip-completed-sims"] else False
startFromCheckpoint = int(args["--start-from-checkpoint"])
startFromCheckpointKeep = int(args["--start-from-checkpoint-keep"])
startFromFrame = int(args["--start-from-frame"])
discardLastFrame = bool(args["--discard-last-frame"])
if startFromCheckpoint != -1:
    start_from_checkpoint.changeInputFiles(testSuite,skipCompletedSims,startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,base)
    sys.exit()
    
os.makedirs(base,exist_ok=True)
basefiles= os.path.expanduser(str(os.path.dirname(os.path.abspath(__file__)))).rstrip("/") if args["--basefiles"] == "False" else os.path.expanduser(str(args["--basefiles"]).rstrip("/"))

myString = stripJsonComments.loadFile(args["--input"])
myString = stripJsonComments.stripComments(myString,kind="all")
stripJsonComments.saveFile(base+"/strippedComments.config",myString)
config = json.loads(myString)
experiments = config.keys()
# this "experiment" is referring to experiments in the experiment.config file,
# each one having an "input" and "output".
for experiment in experiments:  
    ourInput = dict()
    ourOutput = dict()
    configInputKeys = config[experiment]["input"].keys()
    configOutputKeys = config[experiment]["output"].keys()
    
    #this is for the # of runs if we are using an average makespan or pass-fail
    numberOfEach=1
    
    #are we outputting avg-makespan or pass-fail?
    if dictHasKey(config[experiment]["output"],"avg-makespan"):
        #we are outputting avg-makespan, get the # of runs
        numberOfEach=config[experiment]["output"]["avg-makespan"]
        config[experiment]["output"]["makespan"]=True
    elif dictHasKey(config[experiment]["output"],"pass-fail"):
        #we are outputting pass-fail, get the number of runs which is the first number in our list
        #pass-fail list: [runs aka trials, theta, baseline NMTBF, allowed number of failures]
        config[experiment]["input"]["batsim-log"]="information"
        numberOfEach=int(config[experiment]["output"]["pass-fail"][0])

    #here we create the strings for reservations-start, an option to shift the reservation start times for a monte-carlo effect
    resv_start_strings=[]
    if dictHasKey(config[experiment]["output"],"reservations-start"):
        resv_start_config=config[experiment]["output"]["reservations-start"]
        runs_before=0
        runs_after=0
        if dictHasKey(resv_start_config,"runs-before"):
            runs_before=int(resv_start_config["runs-before"])
        if dictHasKey(resv_start_config,"runs-after"):
            runs_after=int(resv_start_config["runs-after"])
        include_base = 0
        if dictHasKey(resv_start_config,"include-base"):
            if resv_start_config["include-base"] == True:
                include_base=1
        numberOfEach=runs_before + runs_after + include_base
        if numberOfEach > 1:
            if dictHasKey(resv_start_config,"orders"):
                for order in resv_start_config["orders"]:
                    if dictHasKey(order,"order-number"):
                        order_num = order["order-number"]
                    if dictHasKey(order,"step-before") or dictHasKey(order,"step-after"):
                        if dictHasKey(order,"step-before"):
                            before_step_seconds = functions.get_seconds_absolute(functions.get_mdhms(order["step-before"]))
                        if dictHasKey(order,"step-after"):
                            after_step_seconds = functions.get_seconds_absolute(functions.get_mdhms(order["step-after"]))
                        for i in range(0,runs_before,1):
                            if len(resv_start_strings)<runs_before:
                                resv_start_strings.append(f"{order_num}:-{before_step_seconds*(i+1)}")
                            else:
                                resv_start_strings[i]=f"{resv_start_strings[i]} , {order_num}:-{before_step_seconds*(i+1)}"
                        for i in range(0,runs_after,1):
                            if len(resv_start_strings)<(runs_before+runs_after):
                                resv_start_strings.append(f"{order_num}:+{after_step_seconds*(i+1)}")
                            else:
                                resv_start_strings[i+runs_before]=f"{resv_start_strings[i+runs_before]} , {order_num}:+{after_step_seconds*(i+1)}"
                    elif dictHasKey(order,"spread-before") or dictHasKey(order,"spread-after"):
                        random = False
                        if dictHasKey(order,"random"):
                            random = order["random"]
                        generated_random_seconds_before=False
                        generated_random_seconds_after=False
                        if dictHasKey(order,"spread-before"):
                            spread_seconds_before = functions.get_seconds_absolute(functions.get_mdhms(order["spread-before"]))
                            if random:
                                seconds_before = np.random.randint(low=1,high=spread_seconds_before,size=runs_before)
                            else:
                                #evenly split up spread-before
                                evenly_split_list=[functions.blockSize(i,runs_before,spread_seconds_before) for i in range(0,runs_before,1)]
                                seconds_before = [np.sum(evenly_split_list[0:i+1]) for i in (range(0,runs_before,1))]
                            count = 0
                            for seconds in seconds_before:
                                if len(resv_start_strings)<runs_before:
                                    resv_start_strings.append(f"{order_num}:-{seconds}")
                                else:
                                    resv_start_strings[count] = f"{resv_start_strings[count]} , {order_num}:-{seconds}"
                                    count+=1
                        if dictHasKey(order,"spread-after"):
                            spread_seconds_after = functions.get_seconds_absolute(functions.get_mdhms(order["spread-after"]))
                            if random:
                                seconds_after = np.random.randint(low=1,high=spread_seconds_after,size=runs_after)
                            else:
                                #evenly split up spread-after
                                evenly_split_list=[functions.blockSize(i,runs_after,spread_seconds_after) for i in range(0,runs_after,1)]
                                seconds_after = [np.sum(evenly_split_list[0:i+1]) for i in (range(0,runs_after,1))]
                            count = 0
                            for seconds in seconds_after:
                                if len(resv_start_strings)<(runs_before + runs_after):
                                    resv_start_strings.append(f"{order_num}:+{seconds}")
                                else:
                                    resv_start_strings[count+runs_before] = f"{resv_start_strings[count+runs_before]} , {order_num}:+{seconds}"
                                    count+=1
    # each i is a key in the "input" section of experiment.config for the given "experiment"
    # could be a sweep or workload or just some property
    for i in configInputKeys:
        if not i.find("-sweep") == -1: # ok we have a sweep
            #what kind of sweep?  The naming convention is NAME-sweep, so get NAME  
            kindOfSweep = i.split("-sweep")[0]
            #make sure it isn't a multiple sweep
            match = re.search(r'[ ]*{[ ]*[0-9]+[ ]*}',str(kindOfSweep))
            if match != None:
                #well we have a multiple sweep, this can now be stripped off the kindOfSweep
                firstPart = str(kindOfSweep)[:match.span()[0]]
                secondPart = str(kindOfSweep)[match.span()[1]+1:]
                kindOfSweep = firstPart + secondPart
            #get the handler for that type of sweep
            handleSweep = sweeps.sweepSwitch(kindOfSweep)
            #execute that sweep's function
            handleSweep(config[experiment]["input"][i],ourInput,config[experiment]["input"])
        elif not i.find("-workload") == -1:  # ok we have a workload, this should be the last option in input, so we can create all workloads below
            #what kind of workload: synthetic or grizzly?
            #The naming convention is NAME-workload, so get the NAME and check its type
            if i.split("-workload",1)[0] == "synthetic":
                #we may have to create the workload, this function deals with all of that
                createWorkload = createSyntheticWorkload
            elif i.split("-workload")[0] == "grizzly":
                #we may have to create a grizzly workload, this function deals with all of that
                createWorkload = createGrizzlyWorkload
            
            #in python we need to be careful what data we are talking about:views/slices, etc..
            # we create a copy here so we don't worry about it pointing back to some original.
            # this data represents all the options in our input->workload section of this config "experiment"
            data = deepcopy(config[experiment]["input"][i])
            
            #get the name of the reservation it uses
            resvName = data["reservations"] if dictHasKey(data, "reservations") else False
            print(f"resvName: {resvName}")
            resv=False
            if resvName:
                resv=deepcopy(config[experiment]["input"]["reservations-%s"%resvName])
                resv=json.dumps(resv)
                
        
            #here we create our platform and workload and get back the location
            #of both of the files and put them into ourInput config
            #here exp is iterating through the experiments of one input in our config, whereas the outer loop - experiments - is iterating over "input"s in our config
            for exp in ourInput.keys():
                nodes = ourInput[exp]["nodes"]
                resv = ourInput[exp]["resv"] if dictHasKey(ourInput[exp],"resv") else resv
                heldback = ourInput[exp]["share-packing-holdback"] if dictHasKey(ourInput[exp],"share-packing-holdback") else -1
                if (not(heldback == -1 )) and args["--increase-heldback-nodes"]:
                    nodes+=heldback
                ids = ourInput[exp]["workload-ids"] if dictHasKey(ourInput[exp],"workload-ids") else -1
                rangeOfIds = [1]
                if not ids == -1:
                    rangeOfIds = parseIds(ids)
                cores = ourInput[exp]["core-count"] if dictHasKey(ourInput[exp],"core-count") else -1
                speeds = ourInput[exp]["speeds"] if dictHasKey(ourInput[exp],"speeds") else -1
                jobs = ourInput[exp]["number-of-jobs"] if dictHasKey(ourInput[exp],"number-of-jobs") else False
                submission_compression = ourInput[exp]["submission-compression"] if dictHasKey(ourInput[exp],"submission-compression") else False
                location = createPlatform(nodes,cores,speeds,basefiles)
                ourInput[exp]["platformFile"]=location
                all_data = deepcopy(ourInput[exp])
                ourInput[exp]={}
                for ourId in rangeOfIds:
                    location,profile_type,machine_speed,submission,command = createWorkload(ourId,submission_compression,data,resv,nodes,jobs,experiment,basefiles,exp,base)
                    ourInput[exp][ourId]=deepcopy(all_data)
                    ourInput[exp][ourId][i]={"workloadFile":location,"profileType":profile_type,"speed":machine_speed,"submissionTime":submission,"command":command}
                


        else:
           # anything that isn't a sweep gets applied here to all jobs in the experiment
            for exp in ourInput.keys():
                data = deepcopy(ourInput[exp])
                data[i] = config[experiment]["input"][i]
                #add in test-suite and skip-completed-sims options
                data["test-suite"]=testSuite
                data["skip-completed-sims"]=skipCompletedSims
                ourInput[exp] = data
                
    #our config is ready, now make the correct directory structure and output the tailored config files
    #for each simulation
    for i in ourInput.keys():
        #where are all these folders going?  --output + experiment + job(i) + id_j + Run_#(number)
        new_base_orig = base +"/" + experiment + "/" + i
        # j is our workload ids
        for j in ourInput[i].keys():
            new_base = new_base_orig + "/" + "id_"+str(j)
            #added for avg-makespan and pass-fail, and reservations-start. loops to create a folder for each Run
            for number in range(1,numberOfEach+1,1):
                run="/Run_"+str(number)
                os.makedirs(new_base + run + "/input",exist_ok=True)
                os.makedirs(new_base + run + "/output",exist_ok=True)
                path=pathlib.Path(__file__).parent.absolute()

                #add in reservations-start
                length_strings = len(resv_start_strings)
                if length_strings > 0:
                    assert (numberOfEach - length_strings) in [0,1] , "Error, length of resv_start_strings is not consistant with the number of runs"
                    if ((numberOfEach - length_strings) == 1) and (number > 1):
                        ourInput[i][j]["reservations-start"]=resv_start_strings[number-2]
                    elif((numberOfEach - length_strings) == 0):
                        ourInput[i][j]["reservations-start"]=resv_start_strings[number-1]
                    
                        


                #batch-job-memory wasn't being observed on our cluster
                #it WAS being observed on a previous machine
                #But ignore this part
                if dictHasKey(ourInput[i],"batch-job-memory"):
                    mem=ourInput[i]["batch-job-memory"]
                    lines=[]
                    count=0
                    with open(new_base + run + "/experiment.sh","r") as InFile:
                        lines=InFile.readlines()
                    for line in lines:
                        if not line.find("--mem=")== -1:
                            lines[count]="#SBATCH --mem="+mem+"\n"
                        count+=1
                    with open(new_base + run + "/experiment.sh","w") as OutFile:
                        OutFile.writelines(lines)

                #write out our output config file
                with open(new_base + run + "/output/config.ini","w")as OutConfig:
                    json.dump(config[experiment]["output"],OutConfig,indent=4)

                #write out our input config file
                with open(new_base + run + "/input/config.ini","w") as OutConfig:
                    json.dump(ourInput[i][j],OutConfig,indent=4)
                #if we set an SMTBF, it may be handy to know the NMTBF when it comes time to output the files.txt file

                if dictHasKey(ourInput[i][j],"nodes") and dictHasKey(ourInput[i],"SMTBF"):
                    ourInput[i]["NMTBF"]=ourInput[i][j]["nodes"]*ourInput[i][j]["SMTBF"]
            #this file tells us with a quick glance what each job has for a config file
            with open(base + "/files.txt","a") as OutFile:
                json.dump(ourInput,OutFile,indent=4)
#this outputs the original config file that was passed as input to this script in the --output folder
if args["--output-config"]:
    copy2(args["--input"],base+"/")
