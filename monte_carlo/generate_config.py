"""
Usage:
    generate_config.py --config-info <type>
    generate_config.py -i FILE -o PATH [--basefiles PATH] [--output-config]

Required Options 1:
    --config-info <type>                Display how the json config is supposed to look like
                                        as well as how each part of it can look like.
                                        <type> can be:
                                                general | sweeps |
                                                node-sweep | SMTBF-sweep | checkpoint-sweep | checkpointError-sweep | performance-sweep |
                                                grizzly-workload | synthetic-workload |
                                                input-options | output
Required Options 2:
    -i <FILE> --input <FILE>            Where our config lives
    -o <PATH> --output <PATH>           Where to start outputing stuff
                                        
Options:
    --basefiles <PATH>                  Where base files go.  Make sure you have a 'workloads' and 'platforms' folder
                                        in this path.
                                        [default: ~/basefiles/]

    --output-config                     If this flag is included, will output the input file to --output directory
                                        as --input filename

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
    
###########################################################################################################    
####                                                                                                  #####
####                                 Create a synthetic workload                                      #####
####                                                                                                  #####
###########################################################################################################		

def createSyntheticWorkload(config,nodes,experiment,basefiles):
    homePath = os.environ['HOME']
    
    if basefiles:
        path= basefiles+"/workloads"
        scriptPath=basefiles
    else:
        path = homePath+"/basefiles/workloads"
        scriptPath = homePath + "/basefiles"
    numberOfJobs=int(config['number-of-jobs']) if dictHasKey(config,'number-of-jobs') else False
    numberOfResources=config['number-of-resources'] if dictHasKey(config,'number-of-resources') else False
    durationTime = config['duration-time'] if dictHasKey(config,'duration-time') else False
    submission=config['submission-time'] if dictHasKey(config,'submission-time') else False
    wallclockLimit = config['wallclock-limit'] if dictHasKey(config,'wallclock-limit') else False
    readtime = config['read-time'] if dictHasKey(config,'read-time') else False
    dumptime = config['dump-time'] if dictHasKey(config,'dump-time') else False
    checkpoint = config['checkpoint-interval'] if dictHasKey(config,'checkpoint-interval') else False
    scaleWidths=int(config['scale-widths-based-on']) if dictHasKey(config,'scale-widths-based-on') else False
    scaleTimeWidth=int(config['scale-time-width-based-on']) if dictHasKey(config,'scale-time-width-based-on') else False
    # if we are scaling widths we need a workload to be based on the original "scale-widths-based-on", notice location2 is the same as location
    # except location2 has scaleWidths for nodes
    if not type(scaleWidths) == bool:
        location2 = "{path}/{nodes}n_{jobs}j_{resources}res_{durationTime}dur_{scaleWidths}_scl_{scaleTimeWidth}_sclTW_{submission}s_{limit}lim_{dumptime}D_{readtime}R_{experiment}_e_synth.json".format(path=path,
                 nodes=scaleWidths,scaleTimeWidth=scaleTimeWidth,jobs=numberOfJobs,resources=nocolon(numberOfResources),durationTime=nocolon(durationTime),scaleWidths=scaleWidths,submission=nocolon(submission),
                limit=nocolon(wallclockLimit),dumptime=nocolon(dumptime),readtime=nocolon(readtime),experiment=experiment)
        if not os.path.isfile(location2):
            # we must make a workload
            command = """python3 {scriptPath}/generate_synthetic_workload.py
                        --nodes {nodes} --number-of-jobs {jobs} --number-of-resources "{resources}" --duration-time "{duration}"
                        --submission-time "{submission}" --output "{output}"
                      """.format(scriptPath=scriptPath,nodes=scaleWidths,jobs=numberOfJobs, resources=numberOfResources,
                                duration=durationTime, submission=submission,output=location2).replace("\n","")
            # optional options
            if not type(wallclockLimit)== bool:
                command +=""" --wallclock-limit "{wallclockLimit}" """.format(wallclockLimit=wallclockLimit)
            if not type(readtime) == bool:
                command +=""" --read-time "{readtime}" """.format(readtime=readtime)
            if not type(dumptime) == bool:
                command +=""" --dump-time "{dumptime}" """.format(dumptime=dumptime)
            if not type(checkpoint) == bool:
                command +=""" --checkpoint-interval "{checkpoint}" """.format(checkpoint=checkpoint)
            os.system(command)      
    location = "{path}/{nodes}n_{jobs}j_{resources}res_{durationTime}dur_{scaleWidths}_scl_{scaleTimeWidth}_sclTW_{submission}s_{limit}lim_{dumptime}D_{readtime}R_{experiment}_e_synth.json".format(path=path,
                 nodes=nodes,scaleTimeWidth=scaleTimeWidth,jobs=numberOfJobs,resources=nocolon(numberOfResources),durationTime=nocolon(durationTime),scaleWidths=scaleWidths,submission=nocolon(submission),
                limit=nocolon(wallclockLimit),dumptime=nocolon(dumptime),readtime=nocolon(readtime),experiment=experiment)
    workloads=[path+"/"+i for i in os.listdir(path) if os.path.isfile(path+"/"+i)]
    if not location in workloads:  # ok location was not already made in workloads, we may have to create a workload
        if len(workloads)>0:
            print(str(path+"/"),flush=True)
            modWorkloads = {i:str(path+"/"+i.split("n_",1)[1]) for i in workloads} # workloads without the nodes
            print(modWorkloads)
            modLocation = path + "/" + location.split("n_",1)[1]
            print(modLocation)
        if len(workloads)==0 or not modLocation in modWorkloads.values() or not scaleTimeWidth==False: # ok location was not in workloads and nodes was not the only difference
            # we must make a workload
            command = """python3 {scriptPath}/generate_synthetic_workload.py
                        --nodes {nodes} --number-of-jobs {jobs} --number-of-resources "{resources}" --duration-time "{duration}"
                        --submission-time "{submission}" --output "{output}"
                      """.format(scriptPath=scriptPath,nodes=nodes,jobs=numberOfJobs, resources=numberOfResources,duration=durationTime,
                                submission=submission,output=location).replace("\n","")
            # optional options
            if not type(scaleTimeWidth)== bool:
                command +=""" --scaleTimeWidth {scaleTimeWidth} """.format(scaleTimeWidth=scaleTimeWidth)
            if not type(wallclockLimit)== bool:
                command +=""" --wallclock-limit "{wallclockLimit}" """.format(wallclockLimit=wallclockLimit)
            if not type(readtime) == bool:
                command +=""" --read-time "{readtime}" """.format(readtime=readtime)
            if not type(dumptime) == bool:
                command +=""" --dump-time "{dumptime}" """.format(dumptime=dumptime)
            if not type(checkpoint) == bool:
                command +=""" --checkpoint-interval "{checkpoint}" """.format(checkpoint=checkpoint)
            print(command)
            os.system(command)      
        else: # ok location without the nodes WAS already made, we simply have to modify it for the amount of nodes
            for orig,mod in modWorkloads.items():
                if modLocation == mod:
                    
                    if not type(scaleWidths)==bool:
                        command = "python3 {scriptPath}/change_workload.py -i {location2} -o {location} --nodes {nodes} --scale-widths-based-on {scaleWidths}".format(
                            scriptPath=scriptPath,location2=location2,location=location,nodes=nodes,scaleWidths=scaleWidths)
                    else:
                        command="python3 {scriptPath}/change_workload.py -i {orig} -o {location} --nodes {nodes}".format(
                            scriptPath=scriptPath,location=location,orig=orig,nodes=nodes)
                    break
            print(command)
            os.system(command)
    return location

###########################################################################################################    
####                                                                                                  #####
####                    Create a workload based on workload data we already had                       #####
####                                                                                                  #####
###########################################################################################################

def createGrizzlyWorkload(config,nodes,experiment,basefiles):
    homePath = os.environ['HOME']
    if basefiles:
        path= basefiles+"/workloads"
        scriptPath=basefiles
    else:
        path = homePath+"/basefiles/workloads"
        scriptPath = homePath + "/basefiles"
  
    time = config['time']
    inputPath=config['input']
    numberOfJobs=int(config['number-of-jobs']) if dictHasKey(config,'number-of-jobs') else False
    scaleWidths=int(config['scale-widths-based-on']) if dictHasKey(config,'scale-widths-based-on') else False
    randomSelection = config['random-selection'] if dictHasKey(config,'random-selection') else False
    wallclockLimit = config['wallclock-limit'] if dictHasKey(config,'wallclock-limit') else False
    submission=config['submission-time'] if dictHasKey(config,'submission-time') else False
    readtime = config['read-time'] if dictHasKey(config,'read-time') else False
    dumptime = config['dump-time'] if dictHasKey(config,'dump-time') else False
    checkpoint = config['checkpoint-interval'] if dictHasKey(config,'checkpoint-interval') else False
    location2=""
   
    # if we are scaling widths we need a workload to be based on the original "scale-widths-based-on", notice location2 is the same as location
    # except location2 has scaleWidths for nodes
    if not type(scaleWidths) == bool:
        location2 = "{path}/{nodes}n_{jobs}j_{submission}s_{readtime}R_{dumptime}D_{checkpoint}chk_{time}t_{randomSelection}rndsel_{wallclockLimit}wcLim_{experiment}_exp_grizzly.json".format(
        path = path,nodes=scaleWidths,jobs=numberOfJobs,submission=nocolon(submission),readtime=nocolon(readtime),dumptime=nocolon(dumptime),
        checkpoint=nocolon(checkpoint),time=nocolon(time),randomSelection=randomSelection,wallclockLimit=nocolon(wallclockLimit),experiment=experiment)
        if not os.path.isfile(location2):
            # we must make a workload
            command = """python3 {scriptPath}/generate_grizzly_workload.py
            --time '{time}' --nodes {nodes} -i {inputPath} -o {outputFile}""".format(scriptPath=scriptPath,time=time,nodes=nodes,
            inputPath=inputPath,outputFile=location2).replace("\n","")
            if not type(submission) == bool:
                command +=" --submission-time {submission}".format(submission=submission)
            if not type(readtime) == bool:
                command +=" --read-time {readtime}".format(readtime=readtime)
            if not type(dumptime) == bool:
                command +=" --dump-time {dumptime}".format(dumptime=dumptime)
            if not type(checkpoint) == bool:
                command +=" --checkpoint-interval {checkpoint}".format(checkpoint=checkpoint)
            if not type(numberOfJobs) == bool:
                command +=" --number-of-jobs {numJobs}".format(numJobs=numberOfJobs)
            if randomSelection:
                command+=" --random-selection"
            if not type(wallclockLimit)== bool:
                command +=" --wallclock-limit {wallclockLimit}".format(wallclockLimit=wallclockLimit)
            os.system(command)

    location = "{path}/{nodes}n_{jobs}j_{submission}s_{readtime}R_{dumptime}D_{checkpoint}chk_{time}t_{randomSelection}rndsel_{wallclockLimit}wcLim_{experiment}_exp_grizzly.json".format(
        path = path,nodes=nodes,jobs=numberOfJobs,submission=nocolon(submission),readtime=nocolon(readtime),dumptime=nocolon(dumptime),
        checkpoint=nocolon(checkpoint),time=nocolon(time),randomSelection=randomSelection,wallclockLimit=nocolon(wallclockLimit),experiment=experiment)
    workloads=[path+"/"+i for i in os.listdir(path) if os.path.isfile(path+"/"+i)]
    if not location in workloads:  # ok location was not already made in workloads, we may have to create a workload
        if len(workloads)>0:
            modWorkloads = {i:path+"/"+i.split("n_",1)[1] for i in workloads} # workloads without the nodes part of the string
            modLocation = path + "/" + location.split("n_",1)[1]  #what the filename we are looking for would be without the nodes as part of the string
        if len(workloads)==0 or not modLocation in modWorkloads.values(): # ok location was not in workloads and nodes was not the only difference
            # we must make a workload
            command = """python3 {scriptPath}/generate_grizzly_workload.py
            --time '{time}' --nodes {nodes} -i {inputPath} -o {outputFile}""".format(scriptPath=scriptPath,time=time,nodes=nodes,
            inputPath=inputPath,outputFile=location).replace("\n","")
            if not type(submission) == bool:
                command +=" --submission-time {submission}".format(submission=submission)
            if not type(readtime) == bool:
                command +=" --read-time {readtime}".format(readtime=readtime)
            if not type(dumptime) == bool:
                command +=" --dump-time {dumptime}".format(dumptime=dumptime)
            if not type(checkpoint) == bool:
                command +=" --checkpoint-interval {checkpoint}".format(checkpoint=checkpoint)
            if not type(numberOfJobs) == bool:
                command +=" --number-of-jobs {numJobs}".format(numJobs=numberOfJobs)
            if randomSelection:
                command+=" --random-selection"
            if not type(wallclockLimit)== bool:
                command +=" --wallclock-limit {wallclockLimit}".format(wallclockLimit=wallclockLimit)
            os.system(command)
        else: # ok location without the nodes WAS already made, we simply have to modify it for the amount of nodes
            for orig,mod in modWorkloads.items():
                if modLocation == mod:
                  if not type(scaleWidths)==bool:
                    command = "python3 {scriptPath}/change_workload.py -i {location2} -o {location} --nodes {nodes} --scale-widths-based-on {scaleWidths}".format(
                      scriptPath=scriptPath,location2=location2,location=location,nodes=nodes,scaleWidths=scaleWidths)
                  else:
                      command="python3 {scriptPath}/change_workload.py -i {orig} -o {location} --nodes {nodes}".format(
                          scriptPath=scriptPath,location=location,orig=orig,nodes=nodes)
                  os.system(command)
    return location

###########################################################################################################    
####                                                                                                  #####
####                  Create a platform file ( just changing # nodes )                                #####
####                                                                                                  #####
###########################################################################################################

def createPlatform(nodes,basefiles):
    
    homePath = os.environ['HOME']
    if basefiles:
        path= basefiles+"/platforms"
        scriptPath=basefiles
    else:
        path = homePath+"/basefiles/platforms"
        scriptPath = homePath + "/basefiles"
    outputPath ="{path}/platform_{nodes}.xml".format(path=path,nodes=nodes)
    inPath="{path}/platform_1490.xml".format(path=path)
    if not os.path.exists(outputPath):
        command = "python3 {scriptPath}/change_platform.py -i {inPath} -o {outputPath} --nodes {nodes}".format(
            scriptPath=scriptPath,nodes=nodes,outputPath=outputPath,inPath=inPath)
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
base = args["--output"].rstrip('/')
basefiles= os.path.expanduser("~/basefiles") if args["--basefiles"]=='~/basefiles/' else args["--basefiles"]
basefiles=basefiles.rstrip('/')
with open(args["--input"],"r") as InConfig:
    config = json.load(InConfig)
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
                
    # each i is a key in the "input" section of experiment.config for the given "experiment"
    # could be a sweep or workload or just some property
    for i in configInputKeys:
        if not i.find("-sweep") == -1: # ok we have a sweep
            #what kind of sweep?  The naming convention is NAME-sweep, so get NAME  
            kindOfSweep = i.split("-sweep")[0]
            #get the handler for that type of sweep
            handleSweep = sweepSwitch(kindOfSweep)
            #execute that sweep's function
            handleSweep(config[experiment]["input"][i],ourInput)
        elif not i.find("-workload") == -1:  # ok we have a workload
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
            data = config[experiment]["input"][i].copy()
            
            #here we create our platform and workload and get back the location
            #of both of the files and put them into ourInput config
            for exp in ourInput.keys():
                nodes = ourInput[exp]["nodes"]
                location = createPlatform(nodes,basefiles)
                ourInput[exp]["platformFile"]=location
                location = createWorkload(data,nodes,experiment,basefiles)
                ourInput[exp][i]={"workloadFile":location}

        else:
           # anything that isn't a sweep gets applied here to all jobs in the experiment
            for exp in ourInput.keys():
                data = ourInput[exp].copy()
                data[i] = config[experiment]["input"][i]
                ourInput[exp] = data
                
    #our config is ready, now make the correct directory structure and output the tailored config files
    #for each simulation
    for i in ourInput.keys():
        #where are all these folders going?  --output + experiment + job(i) + Run_#(number)
        new_base = base +"/" + experiment + "/" + i
        #added for avg-makespan and pass-fail, loops to create a folder for each Run
        for number in range(1,numberOfEach+1,1):
            run="/Run_"+str(number)
            os.makedirs(new_base + run + "/input")
            os.makedirs(new_base + run + "/output")
            path=pathlib.Path(__file__).parent.absolute()
            
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
                json.dump(ourInput[i],OutConfig,indent=4)
            #if we set an SMTBF, it may be handy to know the NMTBF when it comes time to output the files.txt file
            if dictHasKey(ourInput[i],"nodes") and dictHasKey(ourInput[i],"SMTBF"):
                ourInput[i]["NMTBF"]=ourInput[i]["nodes"]*ourInput[i]["SMTBF"]
        #this file tells us with a quick glance what each job has for a config file
        with open(base + "/files.txt","a") as OutFile:
            json.dump(ourInput,OutFile,indent=4)
#this outputs the original config file that was passed as input to this script in the --output folder
if args["--output-config"]:
    copy2(args["--input"],base+"/")
