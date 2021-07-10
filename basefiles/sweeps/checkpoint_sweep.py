from sweeps.sweepFunctions import *
import numpy as np

def checkpointSweep(checkpointSweepInput,ourInput):
    myRange = checkpointSweepInput["range"] if dictHasKey(checkpointSweepInput,"range") else False
    if type(myRange) == bool:
        minimum = checkpointSweepInput["min"]
        maximum = checkpointSweepInput["max"]
        step = checkpointSweepInput["step"] if dictHasKey(checkpointSweepInput,"step") else False
        stepPercent = checkpointSweepInput["step-percent"] if dictHasKey(checkpointSweepInput,"step-percent") else False
        if stepPercent:
            step = np.ceil(stepPercent * minimum).astype('int')
        if not step:
            #there was no step, print error and quit
            print("Error, config file: checkpoint-sweep but no step")
            sys.exit(1) 
        checkpointRange = list(range(minimum,maximum+step,step))
    else:
        checkpointRange = myRange
    currentExperiments = len(ourInput.keys())
    #if there were no sweeps before  
    if currentExperiments == 0: 
        count = 1
        for i in checkpointRange:
            ourInput["experiment_{count}".format(count=count)]={"checkpoint-interval":i}
            count+=1
    #there were sweeps before
    else:
        tmpInput = ourInput.copy()
        count = 1
        # update the current experiments first
        for i in ourInput.keys():
            data = ourInput[i].copy()
            data["checkpoint-interval"] = checkpointRange[0]
            ourInput[i] = data
            count+=1
        for i in checkpointRange:
            if not i == checkpointRange[0]:  #skip the first, we already did it
                for j in tmpInput.keys():
                    data = tmpInput[j].copy()
                    data["checkpoint-interval"] = i
                    ourInput["experiment_{count}".format(count=count)] = data
                    count+=1
