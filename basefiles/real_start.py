#!/usr/bin/env python3
"""
Usage:
    real_start.py --path <PATH> --method <STR> [--socketCount INT][--sim-time INT][--only-output][--requeue-num INT]

Required Options:
    --path <PATH>            Where experiment lives (up to and including the Run_# folder)

    --method <STR>           Method of running batsim:
                             'bare-metal' | 'docker' | 'charliecloud'

Optional Options:
    --socketCount INT        What number socket to use
                             [default: 28000]

    --sim-time INT           How long to run the simulation for in seconds
                             [default: 31536000]

    --requeue-num INT        What requeue num are we doing.  Should be set automatically with 
                             'checkpoint-batsim-requeue':true in config file.
                             [default: 0]
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
import fcntl
import functions
import signal
import subprocess
import psutil
import time
import re
from contextlib import contextmanager
SKIP_GLOBAL_PROGRESS=True
print(" ".join(sys.argv),flush=True)

def acquireLock(locked_file):
    @contextmanager
    def timeout(seconds):
        def timeout_handler(signum, frame):
            # Now that flock retries automatically when interrupted, we need
            # an exception to stop it
            # This exception will propagate on the main thread, make sure you're calling flock there
            raise InterruptedError

        original_handler = signal.signal(signal.SIGALRM, timeout_handler)

        try:
            signal.alarm(seconds)
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, original_handler)
    ''' acquire exclusive lock file access '''
    with timeout(10):
        locked_file_descriptor = open(locked_file, 'w+')
        try:
            fcntl.lockf(locked_file_descriptor, fcntl.LOCK_EX)
            return locked_file_descriptor
        except InterruptedError:
            print("Lock not acquired, skipping")
            raise InterruptedError

def releaseLock(locked_file_descriptor):
    ''' release exclusive lock file access '''
    locked_file_descriptor.close()


def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
def signal_handler(signum,frame):
    try:
        children = psutil.Process(myProcess.pid).children(recursive=True)
        for child in children:
            if child.name()=="batsched":
                child.send_signal(checkpointBatsimSignal)
                break
    except psutil.NoSuchProcess:
        pass

blankline = re.compile("^[ \t]*$")
closingBrace = re.compile("^[ \t]*[}][ \t]*$")
noStatus = re.compile("^[ \t]*\"[a-zA-Z0-9_/-]+\"[ \t]*[:][ \t]*$")
endingComma = re.compile("^[ \t]*\"[a-zA-Z0-9_/-]+\"[ \t]*[:][ \t]*[0-9][ \t]*[,][ \t]*$")

#checks to see if progress file is valid and if not attempts to fix it
#expects that if there is a closing brace, it is on its own line
def getProgress(InOutFile):
    global skipCurrentProgress
    global progress
    skipCurrentProgress = False
    try:
        progress=json.load(InOutFile)
    except:
        #regEX=re.compile("(?:(?:[{}])|(?:\"[a-zA-Z0-9_/-]+\"[:][0-9][,])|(?:\"[a-zA-Z0-9_/-]+\"[:][0-9]))")
        InOutFile.seek(0)
        jsonString = ""
        lines = InOutFile.readlines()
        #fix ending lines

        gotClosingBrace = False
        for i in range(len(lines)-1,-1,-1):
            if blankline.match(lines[i]) != None:
                continue
            if closingBrace.match(lines[i]) != None:
                gotClosingBrace = True
                continue
            elif noStatus.match(lines[i]) != None:
                line = lines[i].rstrip('\n')
                lines[i]=f"{line}0\n"
                if not gotClosingBrace:
                    lines.append('}')
                break
            elif endingComma.match(lines[i]) != None:
                line = lines[i].rstrip('\n').rstrip(',')
                lines[i]=f"{line}\n"
                if not gotClosingBrace:
                    lines.append('}')
                break
        jsonString = "".join(lines)
        try:
            progress=json.loads(jsonString)
        except:
            print("nope")
            skipCurrentProgress=True
def make_gen_command():
    print("making genCommand",flush=True)
    wrapper=""
    if method == "charliecloud":
        wrapper="""USER={USER} {scriptPath}/../charliecloud/charliecloud/bin/ch-run {scriptPath}/../batsim_ch --bind {scriptPath}/../:/mnt/prefix --bind {dirname}:/mnt/FOLDER1 --write --set-env=TERM=xterm-256color --set-env=HOME=/home/sim -- /bin/bash -c "export USER=sim;source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; """.format(scriptPath=scriptPath,dirname=dirname,USER=USER)
        genCommand="""{chPath}/experiment.yaml
        --output-dir={output}/expe-out
        --batcmd=\'batsim {batsimCMD}\'
        --schedcmd=\'batsched {batschedCMD}\'
        --failure-timeout=120
        --ready-timeout=31536000
        --simulation-timeout={mySimTime}
        --success-timeout=300""".format(mySimTime=str(mySimTime),chPath=chPath+"/input",output=chPath+"/output",batsimCMD=functions.batsimCMD,batschedCMD=functions.batschedCMD).replace("\n","")
        mvFolderPath = f"{path}/output"
        myGenCmd="""{wrapper} robin generate {genCommand}" """.format(wrapper=wrapper,genCommand=genCommand)
        mySimCmd=""" {wrapper} robin {yamlPath}" """.format(wrapper=wrapper,yamlPath=chPath+"/input/experiment.yaml")
        postCmd = """{wrapper} python3 {location}/post-processing.py
        -i {path}" """.format(wrapper=wrapper,location="/mnt/prefix/basefiles",path=chPath).replace("\n","")
    elif method == "docker":
        genCommand="""{outPutPath}/experiment.yaml
        --output-dir={output}/expe-out
        --batcmd=\"batsim {batsimCMD}\"
        --schedcmd=\"batsched {batschedCMD}\"
        --failure-timeout=120
        --ready-timeout=31536000
        --simulation-timeout={mySimTime}
        --success-timeout=300""".format(mySimTime=str(mySimTime),outPutPath=path+"/input",output=path+"/output",batsimCMD=functions.batsimCMD,batschedCMD=functions.batschedCMD).replace("\n","")
        mvFolderPath = f"{path}/output"
        myGenCmd="robin generate {genCommand}".format(genCommand=genCommand)
        mySimCmd="robin {yamlPath}".format(yamlPath=path+"/input/experiment.yaml")
        postCmd = """python3 {location}/post-processing.py
        -i {path}""".format(location="/home/sim/simulator/basefiles",path=path).replace("\n","")
    elif method == "bare-metal":
        wrapper=f". {scriptPath}/batsim_environment.sh; "
        genCommand="""{outPutPath}/experiment.yaml
        --output-dir={output}/expe-out
        --batcmd=\"batsim {batsimCMD}\"
        --schedcmd=\"batsched {batschedCMD}\"
        --failure-timeout=120
        --ready-timeout=31536000
        --simulation-timeout={mySimTime}
        --success-timeout=300""".format(mySimTime=str(mySimTime),outPutPath=path+"/input",output=path+"/output",batsimCMD=functions.batsimCMD,batschedCMD=functions.batschedCMD).replace("\n","")
        mvFolderPath = f"{path}/output"
        myGenCmd=f"{wrapper} robin generate {genCommand}"
        mySimCmd=f"{wrapper} robin {path+'/input/experiment.yaml'}"
        postCmd = """{wrapper} python3 {location}/post-processing.py
        -i {path}""".format(wrapper=wrapper,location=scriptPath,path=path).replace("\n","")
    return wrapper,mvFolderPath,myGenCmd,mySimCmd,postCmd
    
#----------------   Main  ------------------------
try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)
USER=os.getenv("USER")
path = args["--path"].rstrip("/")
onlyOutput = args["--only-output"]
basename=""
dirname=""
rest_of_path=""
skipCurrentProgress = False
progress=""
if path.find(":PATH:") != -1:
    basename=os.path.basename(path.split(":PATH:")[0])
    dirname=os.path.dirname(path.split(":PATH:")[0])
    rest_of_path=path.split(":PATH:")[1]
    path = path.replace(":PATH:","")
    progress_path=f"{dirname}/{basename}"
else:
    dirname=os.path.dirname(path)   #id_#
    for i in range(3):
        dirname=os.path.dirname(dirname) # experiment_#, exp, project folder
    basename=os.path.basename(dirname) #project folder
    dirname=os.path.dirname(dirname)  # above project folder
    rest_of_path=path.replace(f"{dirname}/{basename}","")
    progress_path=f"{dirname}/{basename}"
chPath=f"/mnt/FOLDER1/{basename}{rest_of_path}"
locked_file=f"{dirname}/{basename}/progress.lock"
requeue = False
print("after locked_file")
method = args["--method"]
scriptPath = str(pathlib.Path(__file__).parent.absolute())

location = str(os.path.dirname(os.path.abspath(__file__)))
print(path,flush=True)
socketCount=int(args["--socketCount"])
mySimTime=int(args["--sim-time"])
checkpointBatsimSignal=35
functions.batsimOptions={"-s":[f"tcp://localhost:{socketCount}"]}
functions.batschedOptions={"-s":[f"tcp://*:{socketCount}"]}
functions.batsimCMD=""
functions.batschedCMD=""

if method == "charliecloud":
    functions.batsimOptions["-e"]=[f"{chPath}/output/expe-out/out"]
else:
    functions.batsimOptions["-e"]=[f"{path}/output/expe-out/out"]

with open(path+"/input/config.ini","r") as InFile:
    InConfig = json.load(InFile)
with open(scriptPath+"/configIniSchema.json","r") as InFile:
    InSchema = json.load(InFile)
functions.applyJsonSchema(InConfig,InSchema)
globals().update(functions.realStartOptions)
signal.signal(checkpointBatsimSignal,signal_handler)
#testSuite gets defined in configIniSchema.json
if testSuite:
    progress_path = dirname
    locked_file = f"{dirname}/progress.lock"

if not os.path.exists(f"{path}/output/progress.log"):
    myJson="""
    {
        "completed":false
    }
    """
    with open(f"{path}/output/progress.log","w") as OutFile:
        json.dump(json.loads(myJson),OutFile,indent=4)
#skipCompletedSims gets defined in configIniSchema.json
skipCurrentProgress = False

if skipCompletedSims or requeue:
    with open(f"{path}/output/progress.log","r") as InFile:
        progressJson=json.load(InFile)
        if progressJson["completed"]:
            print("ATTN: completed already, no work to do")
            if not SKIP_GLOBAL_PROGRESS:
                try:
                    locked_fd = acquireLock(locked_file)
                    #we have the lock
                    with open(f"{progress_path}/current_progress.log","r") as InOutFile:
                        getProgress(InOutFile)
                        if not skipCurrentProgress:
                            progress[f"{dirname}/{basename}{rest_of_path}_sim"]=1
                            with open(f"{progress_path}/current_progress.log","w") as InOutFile:
                                json.dump(progress,InOutFile,indent=4)
                    releaseLock(locked_fd)
                except InterruptedError:
                    pass
            if dictHasKey(progressJson,"post-processing"):
                sys.exit(0)
            else:
                onlyOutput=True

with open(f"{path}/output/progress.log","r") as InFile:
        progressJson=json.load(InFile)
if not onlyOutput:
    progressJson["completed"]=False
with open(f"{path}/output/progress.log","w") as OutFile:
    json.dump(progressJson,OutFile,indent=4)



myProcess=None
print("finished making batsimCMD and batschedCMD")
print(functions.batsimCMD)
print(functions.batschedCMD)

#---------------------------------- Making gen commands ------------------------------------------
wrapper,mvFolderPath,myGenCmd,mySimCmd,postCmd = make_gen_command()
#-------------------------------------------------------------------------------------------------

#-----------------------------   Move Frame Ahead If Starting From Checkpoint ----------------------
print("real_start.py, finished making genCommand and myGenCmd",flush=True)
print(myGenCmd,flush=True)
if not onlyOutput:
    #startFromXXX and discardLastFrame variables are made available from functions.applyJsonSchema
    #check that the frame exists and move the frame ahead if starting from a checkpoint
    if startFromCheckpoint:
        checkpoint_path = f"{path}/output"
        if (startFromFrame == 0) and (not discardLastFrame):
            checkpoint_path = f"{checkpoint_path}/expe-out/checkpoint_{startFromCheckpoint}"
        elif (not discardLastFrame):
            checkpoint_path = f"{checkpoint_path}/expe-out_{startFromFrame}/checkpoint_{startFromCheckpoint}"
        else:
            checkpoint_path = f"{checkpoint_path}/expe-out_1/checkpoint_{startFromCheckpoint}"
       
        if not os.path.exists(checkpoint_path):
            print(f"ERROR: real_start.py:  '{checkpoint_path}' does not exist")
            sys.exit(1)
        print(f"move_output_folder,startFromCheckpoint:{startFromCheckpoint} startKeep:{startFromCheckpointKeep},startFrame:{startFromFrame}, discard: {discardLastFrame},mvFolderPath,{mvFolderPath},wrapper: {wrapper} ",flush=True)
        start_from_checkpoint.move_output_folder(startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,discardLogs,mvFolderPath,wrapper)
#------------------------------------------------------------------------------------------------------


#---------------------------   Run robin generate and robin experiment.yaml -----------------------------------------
    myProcess = subprocess.Popen(["/usr/bin/bash","-c",myGenCmd])
    myProcess.wait()
    myProcess = subprocess.Popen(["/usr/bin/bash","-c",mySimCmd],preexec_fn=os.setsid)
    myProcess.wait()
#---------------------------------------------------------------------------------------------------------------------



#-------------------------------------     Update Current Progress   -------------------------------------------------
    skipCurrentProgress = False
    if myProcess.returncode >1:
        if not SKIP_GLOBAL_PROGRESS:
            try:
                locked_fd = acquireLock(locked_file)
                with open(f"{progress_path}/current_progress.log","r") as InOutFile:
                    getProgress(InOutFile)
                    if not skipCurrentProgress:
                        progress[f"{dirname}/{basename}{rest_of_path}_sim"]=0
                        progress[f"{dirname}/{basename}{rest_of_path}_post"]=0
                    with open(f"{progress_path}/current_progress.log","w") as InOutFile:
                        json.dump(progress,InOutFile,indent=4)
                releaseLock(locked_fd)
            except InterruptedError:
                pass
        sys.exit(myProcess.returncode)
    else:
        if not SKIP_GLOBAL_PROGRESS:
            try:
                locked_fd = acquireLock(locked_file)
                #we have the lock
                with open(f"{progress_path}/current_progress.log","r") as InOutFile:
                    getProgress(InOutFile)
                    if not skipCurrentProgress:
                        progress[f"{dirname}/{basename}{rest_of_path}_sim"]=1
                        with open(f"{progress_path}/current_progress.log","w") as InOutFile:
                            json.dump(progress,InOutFile,indent=4)
                releaseLock(locked_fd)
            except InterruptedError:
                pass
        with open(f"{path}/output/progress.log","r") as InFile:
            try:
                progressJson=json.load(InFile)
            except:
                progressJson=json.loads("{}") 
        progressJson["completed"]=True
        with open(f"{path}/output/progress.log","w") as OutFile:
            json.dump(progressJson,OutFile,indent=4)
#----------------------------------------------------------------------------------------------------------------


#--------------------------------   Run Pass Fail If Set --------------------------------------------------------
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
#-----------------------------------------------------------------------------------------------------------------


#---------------------------------   Call Post-Processing  ------------------------------------
print("real_start.py, call to post-processing.py",flush=True)
print(postCmd,flush=True)
myProcess = subprocess.Popen(["/usr/bin/bash","-c",myGenCmd])
myProcess.wait()
myProcess = subprocess.Popen(["/usr/bin/bash","-c",postCmd])
myReturn = myProcess.wait()
#----------------------------------------------------------------------------------------------


#-------------------------------     Set progress["post-processing"]   ------------------------
if myReturn == 0:
    with open(f"{path}/output/progress.log","r") as InFile:
            progressJson=json.load(InFile)
            progressJson["post-processing"]=True

#----------------------------------------------------------------------------------------------

#-------------------------------     Set Current Progress  -------------------------------------
if myReturn>0:
    if not SKIP_GLOBAL_PROGRESS:
        try:
            locked_fd = acquireLock(locked_file)
                #we have the lock
            with open(f"{progress_path}/current_progress.log","r") as InOutFile:
                getProgress(InOutFile)
                if not skipCurrentProgress:
                    progress[f"{dirname}/{basename}{rest_of_path}_post"]=0
                    with open(f"{progress_path}/current_progress.log","w") as InOutFile:
                        json.dump(progress,InOutFile,indent=4)
            releaseLock(locked_fd)
        except InterruptedError:
            pass
    sys.exit(myReturn)
else:
    with open(f"{path}/output/progress.log","w") as OutFile:
        json.dump(progressJson,OutFile)
    if not SKIP_GLOBAL_PROGRESS:
        try:
            locked_fd = acquireLock(locked_file)
                #we have the lock
            with open(f"{progress_path}/current_progress.log","r") as InOutFile:
                getProgress(InOutFile)
                if not skipCurrentProgress:
                    progress[f"{dirname}/{basename}{rest_of_path}_post"]=1
                    with open(f"{progress_path}/current_progress.log","w") as InOutFile:
                        json.dump(progress,InOutFile,indent=4)
            releaseLock(locked_fd)
        except InterruptedError:
            pass
