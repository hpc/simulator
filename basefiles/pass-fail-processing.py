"""
Usage:
    pass-fail-processing.py -i PATH --duration STRING --allowed-failures INT
    
Required Options:
    -i PATH --input PATH            Where logfile lives
    
    --duration STRING               When X = allowed-failures, this is when greater
                                    than X failures before this time would result in a "fail"
                                    Pictorialy where the following occurs and it is a "pass":
                                    "           |   |           "
                                    "   <=X     |dur|           "                                                      
                                    "           |   |           "
    
    --allowed-failures INT          The amount of failures that can happen before duration, and
                                    the test will be considered a "pass"                                    
"""
        
        
from docopt import docopt,DocoptExit
import os
import sys
import json
import pathlib
from subprocess import PIPE, Popen
def cmdline(command):
    process = Popen( args=command, stdout=PIPE, shell=True, executable='/bin/bash' )
    return process.communicate()[0]
try:
    args=docopt(__doc__,help=True,options_first=False)
except DocoptExit:
    print(__doc__)
    sys.exit(1)
                                
path = str(args["--input"])
duration = float(args["--duration"])
allowed = int(args["--allowed-failures"])
logFile = "{path}/expe-out/log/batsim.log".format(path=path)
numberOfFailures = cmdline("""cat {logFile} | grep "have been killed" | wc -l""".format(logFile=logFile,allowed=allowed))
if int(numberOfFailures) < (allowed+1):
    with open("{path}/expe-out/pass_fail.csv".format(path=path),"w") as OutFile:
        OutFile.write(",pass\n0,-1")
else:        
    
    command = """cat {logFile} | grep "killed" | head -n {not_allowed} | tail -n 1 | awk -F" " '{{print $2}}' | tr -d "]" """.format(logFile=logFile,not_allowed=allowed+1)
    print(command,flush=True)
    time=cmdline(command)
    print("Time: "+str(time)+"     Duration: "+str(duration),flush=True)
    time = int(float(time))
    myPass=1
    if time < duration:
        myPass=0
    with open("{path}/expe-out/pass_fail.csv".format(path=path),"w") as OutFile:
        OutFile.write(",pass\n0,{myPass}".format(myPass=myPass))
                                                                        
