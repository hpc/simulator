# To make a new sweep:
#   add a <name>.py file to /sweeps folder
#   add "from sweeps.<name> import *"  in this file
#   choose what you are going to call the sweep in experiment.config : <name>-sweep
#   add <name> to "functions" below in sweepSwitch definition
#   associate the <name> added to "functions" below to the function that will get called in sweeps.<name>
#   of course, write the function for the sweep in <name>.py

from sweeps.nodesweep import *
from sweeps.SMTBFsweep import *
from sweeps.checkpoint_sweep import *
from sweeps.performance_sweep import *
from sweeps.checkpointError_sweep import *


def sweepSwitch(kindOfSweep):
    functions = {
        "node" : nodeSweep,
        "SMTBF" : SMTBFSweep,
        "checkpoint":checkpointSweep,
        "performance":performanceSweep,
        "checkpointError":checkpointErrorSweep
    }
    return functions[kindOfSweep]

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
