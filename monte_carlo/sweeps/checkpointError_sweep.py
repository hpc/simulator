from sweeps.sweepFunctions import *
import numpy as np

def checkpointErrorSweep(checkpointErrorSweepInput,ourInput):
    myRange = checkpointErrorSweepInput["range"] if dictHasKey(checkpointErrorSweepInput,"range") else False
    if type(myRange) == bool:
        minimum = float(checkpointErrorSweepInput["min"])
        maximum = float(checkpointErrorSweepInput["max"])
        step = float(checkpointErrorSweepInput["step"]) if dictHasKey(checkpointErrorSweepInput,"step") else False
        stepPercent = checkpointErrorSweepInput["step-percent"] if dictHasKey(checkpointErrorSweepInput,"step-percent") else False
        if stepPercent:
            step = np.ceil(stepPercent * minimum).astype('int')
        if not step:
            #there was no step, print error and quit
            print("Error, config file: checkpointError-sweep but no step")
            sys.exit(1) 
        checkpointErrorRange = list(np.arange(minimum,maximum+step,step))
    else:
        checkpointErrorRange = myRange
    currentExperiments = len(ourInput.keys())
    #if there were no sweeps before  
    if currentExperiments == 0: 
        count = 1
        for i in checkpointErrorRange:
            ourInput["experiment_{count}".format(count=count)]={"checkpointError":i}
            count+=1
    #there were sweeps before
    else:
        tmpInput = ourInput.copy()
        count = 1
        # update the current experiments first
        for i in ourInput.keys():
            data = ourInput[i].copy()
            data["checkpointError"] = checkpointErrorRange[0]
            ourInput[i] = data
            count+=1
        for i in checkpointErrorRange:
            if not i == checkpointErrorRange[0]:  #skip the first, we already did it
                for j in tmpInput.keys():
                    data = tmpInput[j].copy()
                    data["checkpointError"] = i
                    ourInput["experiment_{count}".format(count=count)] = data
                    count+=1
