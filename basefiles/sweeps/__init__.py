# To make a new sweep:
#   add a <name>.py file to /sweeps folder
#   choose what you are going to call the sweep in experiment.config : <name>-sweep
#   add <name> to "functions" below in sweepSwitch definition
#   associate the <name> added to "functions" below to the function that will get called in sweeps.<name>
#   of course, write the function for the sweep in <name>.py


from os import listdir
from os.path import dirname
__all__ = [i[:-3] for i in listdir(dirname(__file__)) if not i.startswith('__') and i.endswith('.py')]


def sweepSwitch(kindOfSweep):
    functions = {
        "node" : node_sweep.nodeSweep,
        "SMTBF" : SMTBF_sweep.SMTBFSweep,
        "checkpoint":checkpoint_sweep.checkpointSweep,
        "performance":performance_sweep.performanceSweep,
        "checkpointError":checkpoint_error_sweep.checkpointErrorSweep,
        "repairTime":repair_time_sweep.repairTimeSweep,
        "coreCount":core_count_sweep.coreCountSweep,
        "corePercent":core_percent_sweep.corePercentSweep,
        "sharePackingHoldback":share_packing_holdback_sweep.sharePackingHoldbackSweep,
        "jobs":jobs_sweep.jobsSweep,
        "reservation": reservation_sweep.reservationSweep,
        "queueDepth": queue_depth_sweep.queueDepthSweep,
        "MTTR": MTTR_sweep.MTTRSweep
    }
    return functions[kindOfSweep]

def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False
