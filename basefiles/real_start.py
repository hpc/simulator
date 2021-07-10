"""
Usage:
    real_start.py --path <PATH> [--socketCount INT][--sim-time INT]

Required Options:
    --path <PATH>            Where experiment lives

Optional Options:
    --socketCount INT        What number socket to use
                             [default: 28000]
    --sim-time INT           How long to run the simulation for in seconds
                             [default: 31536000]

"""


from docopt import docopt,DocoptExit
import os
import sys
import json
import pathlib
def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False

try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)

path = args["--path"].rstrip("/")
print(path,flush=True)
socketCount=int(args["--socketCount"])
mySimTime=int(args["--sim-time"])
with open(path+"/input/config.ini","r") as InFile:
    InConfig = json.load(InFile)

scriptPath = pathlib.Path(__file__).parent.absolute()

syntheticWorkload = InConfig['synthetic-workload'] if dictHasKey(InConfig,'synthetic-workload') else False
grizzlyWorkload = InConfig['grizzly-workload'] if dictHasKey(InConfig,'grizzly-workload') else False
nodes = int(InConfig['nodes']) if dictHasKey(InConfig,'nodes') else False
checkpointingOn = InConfig['checkpointing-on'] if dictHasKey(InConfig,'checkpointing-on') else False
SMTBF = float(InConfig['SMTBF']) if dictHasKey(InConfig,'SMTBF') else False
checkpointInterval = str(InConfig['checkpoint-interval']) if dictHasKey(InConfig,'checkpoint-interval') else False
performanceFactor = float(InConfig['performance-factor']) if dictHasKey(InConfig,'performance-factor') else False
calculateCheckpointing = InConfig['calculate-checkpointing'] if dictHasKey(InConfig,'calculate-checkpointing') else False
platformPath = InConfig['platformFile'] if dictHasKey(InConfig,'platformFile') else False
seedFailures = InConfig['seed-failures'] if dictHasKey(InConfig,'seed-failures') else False
batsimLog = InConfig['batsim-log'] if dictHasKey(InConfig,'batsim-log') else "-q"
batschedLog=InConfig['batsched-log'] if dictHasKey(InConfig,'batsched-log') else "--verbosity quiet"
if not batsimLog  == "-q":
    if batsimLog == "information":
        batsimLog = "-v information"
    elif batsimLog == "network-only":
        batsimLog = "-v network-only"
    elif batsimLog == "debug":
        batsimLog = "-v debug"
    else:
        batsimLog = "-q"
if not batschedLog == "--verbosity quiet":
    if batschedLog == "info":
        batschedLog = "--verbosity info"
    elif batschedLog == "silent":
        batschedLog = "--verbosity silent"
    elif batschedLog == "debug":
        batschedLog = "--verbosity debug"
    else:
        batschedLog = "--verbosity quiet"
if not type(syntheticWorkload) == bool:
    workloadPath = syntheticWorkload["workloadFile"] if dictHasKey(syntheticWorkload,'workloadFile') else False
    if type(workloadPath) == bool:
        workloadPath = createSyntheticWorkload(syntheticWorkload,path,scriptPath,nodes)
elif not type(grizzlyWorkload) == bool:
    workloadPath = grizzlyWorkload["workloadFile"] if dictHasKey(grizzlyWorkload,'workloadFile') else False
    if type(workloadPath) == bool:
        workloadPath = createGrizzlyWorkload(grizzlyWorkload,path,scriptPath,nodes)
if type(platformPath) == bool:
    platformPath = createPlatform(path,nodes)
try:
    
    #source_nix="source /home/sim/.nix-profile/etc/profile.d/nix.sh"
    batsimCMD="-s tcp://localhost:{socketCount}".format(socketCount=socketCount)
    batsimCMD+=" -p {platformPath} -w {workloadPath} -e {output}/expe-out/out".format(platformPath=platformPath, workloadPath=workloadPath,output=path+"/output")
   
    batsimCMD+=" --disable-schedule-tracing --disable-machine-state-tracing "
    batsimCMD+=" --enable-dynamic-jobs --acknowledge-dynamic-jobs {batsimLog}".format(batsimLog=batsimLog)
    if checkpointingOn:
        batsimCMD+=" --checkpointing-on"
    if calculateCheckpointing and type(checkpointInterval)==bool:
        batsimCMD+=" --compute_checkpointing"
    elif checkpointInterval == "optimal":
        batsimCMD+=" --compute_checkpointing"
    elif not checkpointInterval == "optimal":
        checkpointInterval = int(checkpointInterval)
        batsimCMD+=" --checkpointing-interval {checkpointInterval}".format(checkpointInterval=checkpointInterval)
    if not type(SMTBF) == bool:
        batsimCMD+=" --SMTBF {SMTBF}".format(SMTBF=SMTBF)
    if seedFailures:
        batsimCMD+=" --seed-failures"
    if not type(performanceFactor) == bool:
        batsimCMD+=" --performance-factor {performanceFactor}".format(performanceFactor=performanceFactor)
    print("finished making batsimCMD",flush=True)
    print(batsimCMD,flush=True)
    print("making genCommand",flush=True)
    genCommand="""{outPutPath}/experiment.yaml  
    --output-dir={output}/expe-out
    --batcmd=\"batsim {batsimCMD}\"
    --schedcmd=\"batsched -v fcfs_fast2 -s tcp://*:{socketCount} {batschedLog}\"
    --failure-timeout=60 
    --ready-timeout=31536000 
    --simulation-timeout={mySimTime}
    --success-timeout=60""".format(batsimLog=batsimLog,batschedLog=batschedLog,mySimTime=str(mySimTime),socketCount=socketCount,outPutPath=path+"/input",output=path+"/output",batsimCMD=batsimCMD).replace("\n","")
    myGenCmd="robin generate {genCommand}".format(genCommand=genCommand)
    print("finished making genCommand and myGenCmd",flush=True)
    print(myGenCmd,flush=True)
    os.system(myGenCmd)
    mySimCmd="robin {yamlPath}".format(yamlPath=path+"/input/experiment.yaml")
    myReturn = os.system(mySimCmd)
    if myReturn >1:
        sys.exit(myReturn)

    #Output
    with open(path+"/output/config.ini","r") as InFile:
        OutConfig = json.load(InFile)
    AAE = OutConfig['AAE'] if dictHasKey(OutConfig,'AAE') else False
    makespan = OutConfig['makespan'] if dictHasKey(OutConfig,'makespan') else False
    raw = int(OutConfig['raw']) if dictHasKey(OutConfig,'raw') else False
    passFail=OutConfig['pass-fail'] if dictHasKey(OutConfig,'pass-fail') else False
    

    
    location = "/home/sim/basefiles"
    if passFail:
        theta = float(passFail[1])
        baselineSMTBF = int(passFail[2])/float(nodes)
        failures = int(passFail[3])
        duration = str(theta * baselineSMTBF)
        postCmd = """python3 {location}/pass-fail-processing.py -i {logfile} --duration {duration} --allowed-failures {failures}""".format(duration=duration,failures=failures,location=location,logfile=path+"/output")
    else:
        postCmd = """python3 {location}/post-processing.py
        -i {outJobs}""".format(location=location,outJobs=path+"/output/expe-out").replace("\n","")
        if not type(raw) == bool:
            postCmd +=" --raw {raw}".format(raw=raw)
        if checkpointingOn:
            postCmd +=" --checkpointing-on"
        if makespan:
            postCmd+=" --makespan"
    
    print(postCmd,flush=True)
    myReturn = os.system(postCmd)
    if myReturn>1:
        sys.exit(myReturn)


except:
    sys.exit(1)






