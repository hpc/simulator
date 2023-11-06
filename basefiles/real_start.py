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
import start_from_checkpoint
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
basename=""
dirname=""
rest_of_path=""
if not args["--only-output"]:
    basename=os.path.basename(path.split(":PATH:")[0])
    dirname=os.path.dirname(path.split(":PATH:")[0])
    rest_of_path=path.split(":PATH:")[1]
    path = path.replace(":PATH:","")
chPath=f"/mnt/FOLDER1/{basename}{rest_of_path}"



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
MTTR = float(InConfig['MTTR']) if dictHasKey(InConfig,"MTTR") else False
seedRepairTimes = InConfig['seed-repair-times'] if dictHasKey(InConfig, 'seed-repair-times') else False
checkpoint_batsim_interval = InConfig['checkpoint-batsim-interval']if dictHasKey(InConfig,"checkpoint-batsim-interval") else False
submitTimeAfter=str(InConfig['submission-time-after']) if dictHasKey(InConfig,'submission-time-after') else False
submitTimeBefore=str(InConfig['submission-time-before']) if dictHasKey(InConfig,'submission-time-before') else False
copyWorkload = str(InConfig['copy']) if dictHasKey(InConfig,'copy') else False
disableDynamic = bool(InConfig['disable-dynamic-jobs']) if dictHasKey(InConfig,'disable-dynamic-jobs') else False
startFromCheckpoint = int(InConfig['start-from-checkpoint']) if dictHasKey(InConfig,'start-from-checkpoint') else False
startFromCheckpointKeep = int(InConfig["start-from-checkpoint-keep"]) if dictHasKey(InConfig,"start-from-checkpoint-keep") else False
startFromFrame = int(InConfig["start-from-frame"]) if dictHasKey(InConfig,"start-from-frame") else False
discardLastFrame = bool(InConfig["discard-last-frame"]) if dictHasKey(InConfig,"discard-last-frame") else False
checkpointSignal = int(InConfig["checkpoint-batsim-signal"]) if dictHasKey(InConfig,"checkpoint-batsim-signal") else False
checkpointKeep = int(InConfig["checkpoint-batsim-keep"]) if dictHasKey(InConfig,"checkpoint-batsim-keep") else False
outputSvg = InConfig["output-svg"] if dictHasKey(InConfig,'output-svg') else False
outputSvgMethod = InConfig["output-svg-method"] if dictHasKey(InConfig,'output-svg-method') else False
svgFrameStart = int(InConfig["svg-frame-start"]) if dictHasKey(InConfig,'svg-frame-start') else False
svgFrameEnd = int(InConfig["svg-frame-end"]) if dictHasKey(InConfig,"svg-frame-end") else False
svgOutputStart = int(InConfig["svg-output-start"]) if dictHasKey(InConfig,"svg-output-start") else False
svgOutputEnd = int(InConfig["svg-output-end"]) if dictHasKey(InConfig,'svg-output-end') else False


if batschedPolicy == "conservative_bf":
    submitProfiles = True
workloadPath = ""
profileType = ""
speed = ""
if not type(syntheticWorkload) == bool:
    workloadPath = syntheticWorkload["workloadFile"] if dictHasKey(syntheticWorkload,'workloadFile') else False
    profileType = syntheticWorkload["profileType"] if dictHasKey(syntheticWorkload,'profileType') else False
    speed = syntheticWorkload["speed"] if dictHasKey(syntheticWorkload,'speed') else False
    
elif not type(grizzlyWorkload) == bool:
    workloadPath = grizzlyWorkload["workloadFile"] if dictHasKey(grizzlyWorkload,'workloadFile') else False
    profileType = grizzlyWorkload["profileType"] if dictHasKey(grizzlyWorkload,'profileType') else False
    speed = grizzlyWorkload["speed"] if dictHasKey(grizzlyWorkload,"speed") else False



   
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

batsimCMD="-s tcp://localhost:{socketCount}".format(socketCount=socketCount)
if method == "charliecloud":
    batsimCMD+=" -p {platformPath} -w {workloadPath} -e {output}/expe-out/out".format(platformPath=platformPath, workloadPath=workloadPath,output=chPath+"/output")
else:
    batsimCMD+=" -p {platformPath} -w {workloadPath} -e {output}/expe-out/out".format(platformPath=platformPath, workloadPath=workloadPath,output=path+"/output")

batsimCMD+=" --disable-schedule-tracing --disable-machine-state-tracing {batsimLog}".format(batsimLog=batsimLog)
if not disableDynamic:
    batsimCMD+=" --enable-dynamic-jobs --acknowledge-dynamic-jobs"
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
if seedRepairTimes:
    batsimCMD+=" --seed-repair-times"
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
if outputSvg:
    batsimCMD+=f" --output-svg {outputSvg}"
if outputSvgMethod:
    batsimCMD+=f" --output-svg-method {outputSvgMethod}"
if svgFrameStart:
    batsimCMD+=f" --svg-frame-start {svgFrameStart}"
if svgFrameEnd:
    batsimCMD+=f" --svg-frame-end {svgFrameEnd}"
if svgOutputStart:
    batsimCMD+=f" --svg-output-start {svgOutputStart}"
if svgOutputEnd:
    batsimCMD+=f" --svg-output-end {svgOutputEnd}"
if queueDepth:
    batsimCMD+=" --queue-depth {queueDepth}".format(queueDepth=queueDepth)
if reservationsStart:
    batsimCMD+=" --reservations-start {reservationsStart}".format(reservationsStart=reservationsStart)
if (not type(MTTR) == bool) and (MTTR > 0) :
    batsimCMD+=" --MTTR {MTTR}".format(MTTR=MTTR)
if checkpoint_batsim_interval:
    batsimCMD+=f" --checkpoint-batsim-interval {checkpoint_batsim_interval}"
if startFromCheckpoint:
    batsimCMD+=f" --start-from-checkpoint {startFromCheckpoint}"
    
if checkpointSignal:
    batsimCMD+=f" --checkpoint-batsim-signal {checkpointSignal}"
if checkpointKeep:
    batsimCMD+=f" --checkpoint-batsim-keep {checkpointKeep}"
if copyWorkload:
    batsimCMD+=f" --copy {copyWorkload}"
if submitTimeBefore:
    batsimCMD+=f" --submission-time-before {submitTimeBefore}"
if submitTimeAfter:
    batsimCMD+=f" --submission-time-after {submitTimeAfter}"

print("finished making batsimCMD")
print(batsimCMD)
print("making genCommand",flush=True)
wrapper=""
if method == "charliecloud":
    wrapper="""{scriptPath}/../charliecloud/charliecloud/bin/ch-run {scriptPath}/../batsim_ch --bind {scriptPath}/../:/mnt/prefix --bind {dirname}:/mnt/FOLDER1 --write --set-env=TERM=xterm-256color --set-env=HOME=/home/sim -- /bin/bash -c "export USER=sim;source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; """.format(scriptPath=scriptPath,dirname=dirname)
    genCommand="""{chPath}/experiment.yaml
    --output-dir={output}/expe-out
    --batcmd=\'batsim {batsimCMD}\'
    --schedcmd=\'batsched -v {policy} -s tcp://*:{socketCount} {batschedLog}\'
    --failure-timeout=120
    --ready-timeout=31536000
    --simulation-timeout={mySimTime}
    --success-timeout=300""".format(policy=batschedPolicy,batsimLog=batsimLog,batschedLog=batschedLog,mySimTime=str(mySimTime),socketCount=socketCount,chPath=chPath+"/input",output=chPath+"/output",batsimCMD=batsimCMD).replace("\n","")
    mvFolderPath = f"{chPath}/output"
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
    mvFolderPath = f"{path}/output"
    myGenCmd="robin generate {genCommand}".format(genCommand=genCommand)
    mySimCmd="robin {yamlPath}".format(yamlPath=path+"/input/experiment.yaml")
    postCmd = """python3 {location}/post-processing.py
    -i {path}""".format(location="/home/sim/simulator/basefiles",path=path).replace("\n","")
elif method == "bare-metal":
    genCommand="""{outPutPath}/experiment.yaml
    --output-dir={output}/expe-out
    --batcmd=\"batsim {batsimCMD}\"
    --schedcmd=\"batsched -v {policy} -s tcp://*:{socketCount} {batschedLog}\"
    --failure-timeout=120
    --ready-timeout=31536000
    --simulation-timeout={mySimTime}
    --success-timeout=300""".format(policy=batschedPolicy,batsimLog=batsimLog,batschedLog=batschedLog,mySimTime=str(mySimTime),socketCount=socketCount,outPutPath=path+"/input",output=path+"/output",batsimCMD=batsimCMD).replace("\n","")
    mvFolderPath = f"{path}/output"
    myGenCmd="robin generate {genCommand}".format(genCommand=genCommand)
    mySimCmd="robin {yamlPath}".format(yamlPath=path+"/input/experiment.yaml")
    postCmd = """python3 {location}/post-processing.py
    -i {path}""".format(location=scriptPath,path=path).replace("\n","")

print("real_start.py, finished making genCommand and myGenCmd",flush=True)
print(myGenCmd,flush=True)
if not args["--only-output"]:
    if startFromCheckpoint:
        start_from_checkpoint.move_output_folder(startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,mvFolderPath,wrapper)
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
