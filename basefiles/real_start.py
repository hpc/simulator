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
import fcntl
import functions

def acquireLock(locked_file):
    ''' acquire exclusive lock file access '''
    locked_file_descriptor = open(locked_file, 'w+')
    fcntl.lockf(locked_file_descriptor, fcntl.LOCK_EX)
    return locked_file_descriptor

def releaseLock(locked_file_descriptor):
    ''' release exclusive lock file access '''
    locked_file_descriptor.close()


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
USER=os.getenv("USER")
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
locked_file=f"{dirname}/progress.lock"

print("after locked_file")
method = args["--method"]
scriptPath = str(pathlib.Path(__file__).parent.absolute())

location = str(os.path.dirname(os.path.abspath(__file__)))
print(path,flush=True)
socketCount=int(args["--socketCount"])
mySimTime=int(args["--sim-time"])
functions.batsimOptions={"-s":f"tcp://localhost:{socketCount}"}
functions.batschedOptions={"-s":f"tcp://*:{socketCount}"}
functions.batsimCMD=""
functions.batschedCMD=""

if method == "charliecloud":
    functions.batsimOptions["-e"]=f"{chPath}/output/expe-out/out"
else:
    functions.batsimOptions["-e"]=f"{path}/output/expe-out/out"

with open(path+"/input/config.ini","r") as InFile:
    InConfig = json.load(InFile)
with open(scriptPath+"/configIniSchema.json","r") as InFile:
    InSchema = json.load(InFile)
functions.applyJsonSchema(InConfig,InSchema)
globals().update(functions.realStartOptions)

print("finished making batsimCMD and batschedCMD")
print(functions.batsimCMD)
print(functions.batschedCMD)
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
    -i {path}""".format(location=scriptPath,path=path).replace("\n","")

print("real_start.py, finished making genCommand and myGenCmd",flush=True)
print(myGenCmd,flush=True)
if not args["--only-output"]:
    #startFromXXX and discardLastFrame variables are made available from functions.applyJsonSchema
    if startFromCheckpoint:
        start_from_checkpoint.move_output_folder(startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,mvFolderPath,wrapper)
    os.system(myGenCmd)
    myReturn = os.system(mySimCmd)
    if myReturn >1:
        locked_fd = acquireLock(locked_file)
        with open(f"{dirname}/progress.log","r") as InOutFile:
            progress=json.load(InOutFile)
            progress[f"{dirname}/{basename}{rest_of_path}_sim"]=0
            progress[f"{dirname}/{basename}{rest_of_path}_post"]=0
        with open(f"{dirname}/progress.log","w") as InOutFile:
            json.dump(progress,InOutFile,indent=4)
        releaseLock(locked_fd)
        sys.exit(myReturn)
    else:
        locked_fd = acquireLock(locked_file)
        #we have the lock
        with open(f"{dirname}/progress.log","r") as InOutFile:
            progress=json.load(InOutFile)
            progress[f"{dirname}/{basename}{rest_of_path}_sim"]=1
        with open(f"{dirname}/progress.log","w") as InOutFile:
            json.dump(progress,InOutFile,indent=4)
        releaseLock(locked_fd)
    


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
    locked_fd = acquireLock(locked_file)
        #we have the lock
    with open(f"{dirname}/progress.log","r") as InOutFile:
        progress=json.load(InOutFile)
        progress[f"{dirname}/{basename}{rest_of_path}_post"]=0
    with open(f"{dirname}/progress.log","w") as InOutFile:
        json.dump(progress,InOutFile,indent=4)
    releaseLock(locked_fd)
    sys.exit(myReturn)
else:
    locked_fd = acquireLock(locked_file)
        #we have the lock
    with open(f"{dirname}/progress.log","r") as InOutFile:
        progress=json.load(InOutFile)
        progress[f"{dirname}/{basename}{rest_of_path}_post"]=1
    with open(f"{dirname}/progress.log","w") as InOutFile:
        json.dump(progress,InOutFile,indent=4)
    releaseLock(locked_fd)
