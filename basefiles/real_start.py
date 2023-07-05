"""
Usage:
    real_start.py --path <PATH> --method <STR> [--socketCount INT][--sim-time INT][--only-output]

Required Options:
    --path <PATH>            Where experiment lives

    --method <STR>           Method of running batsim:
                             'bare-metal' | 'docker' | 'charliecloud'

Optional Options:
    --socketCount INT        What number socket to use
                             [default: 28000]

    --sim-time INT           How long to run the simulation for in seconds
                             [default: 31536000]

    --only-output            part of traverse_and_post_process.py. will only
                             do the post-processing, not the simulation.
                             This implies that the simulation was already completed
                             and that there is a '--path'/output/expe-out/out_jobs.csv
                             [default: False]

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
basename=os.path.basename(path.split(":PATH:")[0])
dirname=os.path.dirname(path.split(":PATH:")[0])
rest_of_path=path.split(":PATH:")[1]
chPath=f"/mnt/FOLDER1/{basename}{rest_of_path}"

path = path.replace(":PATH:","")

method = args["--method"]


location = str(os.path.dirname(os.path.abspath(__file__)))
print(path,flush=True)
socketCount=int(args["--socketCount"])
mySimTime=int(args["--sim-time"])
with open(path+"/input/config.ini","r") as InFile:
    InConfig = json.load(InFile)

scriptPath = pathlib.Path(__file__).parent.absolute()

syntheticWorkload = InConfig['synthetic-workload'] if dictHasKey(InConfig,'synthetic-workload') else False
grizzlyWorkload = InConfig['grizzly-workload'] if dictHasKey(InConfig,'grizzly-workload') else False
nodes = int(InConfig['nodes']) if dictHasKey(InConfig,'nodes') else False
cores = int(InConfig['core-count']) if dictHasKey(InConfig,'core-count') else False
speeds = str(InConfig['speeds']) if dictHasKey(InConfig,'speeds') else False
sharePacking = InConfig['share-packing'] if dictHasKey(InConfig,"share-packing") else False
sharePackingHoldback = InConfig['share-packing-holdback'] if dictHasKey(InConfig,"share-packing-holdback") else False
corePercent = float(InConfig['core-percent']) if dictHasKey(InConfig,"core-percent") else False
checkpointingOn = InConfig['checkpointing-on'] if dictHasKey(InConfig,'checkpointing-on') else False
SMTBF = float(InConfig['SMTBF']) if dictHasKey(InConfig,'SMTBF') else False
checkpointInterval = str(InConfig['checkpoint-interval']) if dictHasKey(InConfig,'checkpoint-interval') else False
performanceFactor = float(InConfig['performance-factor']) if dictHasKey(InConfig,'performance-factor') else False
calculateCheckpointing = InConfig['calculate-checkpointing'] if dictHasKey(InConfig,'calculate-checkpointing') else False
platformPath = InConfig['platformFile'] if dictHasKey(InConfig,'platformFile') else False
seedFailures = InConfig['seed-failures'] if dictHasKey(InConfig,'seed-failures') else False
batsimLog = InConfig['batsim-log'] if dictHasKey(InConfig,'batsim-log') else "-q"
batschedLog=InConfig['batsched-log'] if dictHasKey(InConfig,'batsched-log') else "--verbosity quiet"
repairTime = InConfig['repair-time'] if dictHasKey(InConfig,'repair-time') else False
fixedFailures = InConfig['fixed-failures'] if dictHasKey(InConfig,'fixed-failures') else False
checkpointError = InConfig['checkpointError'] if dictHasKey(InConfig,'checkpointError') else False
batschedPolicy = InConfig['batsched-policy'] if dictHasKey(InConfig,'batsched-policy') else False
submitProfiles = InConfig['forward-profiles-on-submission'] if dictHasKey(InConfig,'forward-profiles-on-submission') else False
queueDepth = InConfig['queue-depth'] if dictHasKey(InConfig,'queue-depth') else False
reservationsStart = InConfig['reservations-start'] if dictHasKey(InConfig,'reservations-start') else False


if batschedPolicy == "conservative_bf":
    submitProfiles = True
workloadPath = ""
profileType = ""
speed = ""

if not args["--only-output"]:
   
    if not batsimLog  == "-q":
        if batsimLog == "info" or batsimLog == "information":
            batsimLog = "-v information"
        elif batsimLog == "network-only":
            batsimLog = "-v network-only"
        elif batsimLog == "debug":
            batsimLog = "-v debug"
        else:
            batsimLog = "-q"
    
    if not batschedLog == "--verbosity quiet":
        if batschedLog == "info" or batschedLog == "information":
            batschedLog = "--verbosity info"
        elif batschedLog == "silent":
            batschedLog = "--verbosity silent"
        elif batschedLog == "debug":
            batschedLog = "--verbosity debug"
        else:
            batschedLog = "--verbosity quiet"
    if not type(syntheticWorkload) == bool:
        workloadPath = syntheticWorkload["workloadFile"] if dictHasKey(syntheticWorkload,'workloadFile') else False
        profileType = syntheticWorkload["profileType"] if dictHasKey(syntheticWorkload,'profileType') else False
        speed = syntheticWorkload["speed"] if dictHasKey(syntheticWorkload,'speed') else False
        if type(workloadPath) == bool:
            workloadPath = createSyntheticWorkload(syntheticWorkload,path,scriptPath,nodes)
    elif not type(grizzlyWorkload) == bool:
        workloadPath = grizzlyWorkload["workloadFile"] if dictHasKey(grizzlyWorkload,'workloadFile') else False
        profileType = grizzlyWorkload["profileType"] if dictHasKey(grizzlyWorkload,'profileType') else False
        speed = grizzlyWorkload["speed"] if dictHasKey(grizzlyWorkload,"speed") else False
        if type(workloadPath) == bool:
            workloadPath = createGrizzlyWorkload(grizzlyWorkload,path,scriptPath,nodes)
    if type(platformPath) == bool:
        platformPath = createPlatform(path,nodes,cores,speeds)
    
    #source_nix="source /home/sim/.nix-profile/etc/profile.d/nix.sh"
    batsimCMD="-s tcp://localhost:{socketCount}".format(socketCount=socketCount)
    if method == "charliecloud":
        batsimCMD+=" -p {platformPath} -w {workloadPath} -e {output}/expe-out/out".format(platformPath=platformPath, workloadPath=workloadPath,output=chPath+"/output")
    else:
        batsimCMD+=" -p {platformPath} -w {workloadPath} -e {output}/expe-out/out".format(platformPath=platformPath, workloadPath=workloadPath,output=path+"/output")
    #if not (batschedPolicy == "conservative_bf"):
    batsimCMD+=" --disable-schedule-tracing --disable-machine-state-tracing "
    batsimCMD+=" --enable-dynamic-jobs --acknowledge-dynamic-jobs {batsimLog}".format(batsimLog=batsimLog)
    if checkpointingOn:
        batsimCMD+=" --checkpointing-on"
    if calculateCheckpointing and type(checkpointInterval)==bool:
        batsimCMD+=" --compute_checkpointing"
    elif checkpointInterval == "optimal":
        batsimCMD+=" --compute_checkpointing"
    elif type(checkpointInterval) == bool:
        batsimCMD+=""
    elif not checkpointInterval == "optimal":
        checkpointInterval = int(checkpointInterval)
        batsimCMD+=" --checkpointing-interval {checkpointInterval}".format(checkpointInterval=checkpointInterval)
    if not type(SMTBF) == bool:
        batsimCMD+=" --SMTBF {SMTBF}".format(SMTBF=SMTBF)
    if seedFailures:
        batsimCMD+=" --seed-failures"
    if not type(performanceFactor) == bool:
        batsimCMD+=" --performance-factor {performanceFactor}".format(performanceFactor=performanceFactor)
    if not type(repairTime) == bool:
        batsimCMD+=" --repair-time {repairTime}".format(repairTime=repairTime)
    if not type(fixedFailures) == bool:
        batsimCMD+=" --fixed-failures {fixedFailures}".format(fixedFailures=fixedFailures)
    if not type(checkpointError) == bool:
        batsimCMD+=" --compute_checkpointing_error {checkpointError}".format(checkpointError=checkpointError)
    if sharePacking:
        batsimCMD+=" --share-packing"
        batsimCMD+=" --enable-compute-sharing"
    if sharePackingHoldback:
        batsimCMD+=" --share-packing-holdback {}".format(sharePackingHoldback)
    if not type(corePercent) == bool:
        batsimCMD+=" --core-percent {corePercent}".format(corePercent=corePercent)
    if submitProfiles:
        batsimCMD+=" --forward-profiles-on-submission "
    if queueDepth:
        batsimCMD+=" --queue-depth {queueDepth}".format(queueDepth=queueDepth)
    if reservationsStart:
        batsimCMD+=" --reservations-start {reservationsStart}".format(reservationsStart=reservationsStart)


    print("finished making batsimCMD")
    print(batsimCMD)
    print("making genCommand",flush=True)
    if method == "charliecloud":
        wrapper="""{scriptPath}/../charliecloud/charliecloud/bin/ch-run {scriptPath}/../batsim_ch --bind {scriptPath}/../:/mnt/prefix --bind {dirname}:/mnt/FOLDER1 --write --set-env=TERM=xterm-256color --set-env=HOME=/home/sim -- /bin/bash -c "export USER=sim;source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/python_env/bin/activate; """.format(scriptPath=scriptPath,dirname=dirname)
        genCommand="""{chPath}/experiment.yaml
        --output-dir={output}/expe-out
        --batcmd=\'batsim {batsimCMD}\'
        --schedcmd=\'batsched -v {policy} -s tcp://*:{socketCount} {batschedLog}\'
        --failure-timeout=120
        --ready-timeout=31536000
        --simulation-timeout={mySimTime}
        --success-timeout=300""".format(policy=batschedPolicy,batsimLog=batsimLog,batschedLog=batschedLog,mySimTime=str(mySimTime),socketCount=socketCount,chPath=chPath+"/input",output=chPath+"/output",batsimCMD=batsimCMD).replace("\n","")
        myGenCmd="""{wrapper} robin generate {genCommand}" """.format(wrapper=wrapper,genCommand=genCommand)
        mySimCmd=""" {wrapper} robin {yamlPath}" """.format(wrapper=wrapper,yamlPath=chPath+"/input/experiment.yaml")
        postCmd = """{wrapper} python3 {location}/post-processing.py
        -i {path}" """.format(wrapper=wrapper,location="/mnt/prefix/basefiles",path=chPath).replace("\n","")
    elif method == "docker":
        genCommand="""{outPutPath}/experiment.yaml  
        --output-dir={output}/expe-out
        --batcmd=\"batsim {batsimCMD}\"
        --schedcmd=\"batsched -v {policy} -s tcp://*:{socketCount} {batschedLog}\"
        --failure-timeout=120 
        --ready-timeout=31536000 
        --simulation-timeout={mySimTime}
        --success-timeout=300""".format(policy=batschedPolicy,batsimLog=batsimLog,batschedLog=batschedLog,mySimTime=str(mySimTime),socketCount=socketCount,outPutPath=path+"/input",output=path+"/output",batsimCMD=batsimCMD).replace("\n","")
        myGenCmd="robin generate {genCommand}".format(genCommand=genCommand)
        mySimCmd="robin {yamlPath}".format(yamlPath=path+"/input/experiment.yaml")
        postCmd = """python3 {location}/post-processing.py
        -i {path}""".format(location="/home/sim/basefiles",path=path).replace("\n","")
    elif method == "bare-metal":
        genCommand="""{outPutPath}/experiment.yaml  
        --output-dir={output}/expe-out
        --batcmd=\"batsim {batsimCMD}\"
        --schedcmd=\"batsched -v {policy} -s tcp://*:{socketCount} {batschedLog}\"
        --failure-timeout=120 
        --ready-timeout=31536000 
        --simulation-timeout={mySimTime}
        --success-timeout=300""".format(policy=batschedPolicy,batsimLog=batsimLog,batschedLog=batschedLog,mySimTime=str(mySimTime),socketCount=socketCount,outPutPath=path+"/input",output=path+"/output",batsimCMD=batsimCMD).replace("\n","")
        myGenCmd="robin generate {genCommand}".format(genCommand=genCommand)
        mySimCmd="robin {yamlPath}".format(yamlPath=path+"/input/experiment.yaml")
        postCmd = """python3 {location}/post-processing.py
        -i {path}""".format(location=scriptPath,path=path).replace("\n","")
    print("real_start.py, finished making genCommand and myGenCmd",flush=True)
    print(myGenCmd,flush=True)
    os.system(myGenCmd)
    myReturn = os.system(mySimCmd)
    if myReturn >1:
        sys.exit(myReturn)
    


with open(path+"/output/config.ini","r") as InFile:
    OutConfig = json.load(InFile)
passFail=OutConfig['pass-fail'] if dictHasKey(OutConfig,'pass-fail') else False


#TODO update passFail code
if passFail:
    theta = float(passFail[1])
    baselineSMTBF = int(passFail[2])/float(nodes)
    failures = int(passFail[3])
    duration = str(theta * baselineSMTBF)
    postCmd = """python3 {location}/pass-fail-processing.py -i {logfile} --duration {duration} --allowed-failures {failures}""".format(duration=duration,failures=failures,location=location,logfile=path+"/output")
else:
    print("real_start.py, passFail=False",flush=True)
    

print("real_start.py, call to post-processing.py",flush=True)
print(postCmd,flush=True)
myReturn = os.system(postCmd)
if myReturn>1:
    sys.exit(myReturn)