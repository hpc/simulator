from sweeps.sweepFunctions import *
import numpy as np

def performanceSweep(SweepInput,ourInput,origInput):
    myRange = SweepInput["range"] if dictHasKey(SweepInput,"range") else False
    if type(myRange) == bool:
        minimum = float(SweepInput["min"])
        maximum = float(SweepInput["max"])
        step = SweepInput["step"] if dictHasKey(SweepInput,"step") else False
        stepPercent = SweepInput["step-percent"] if dictHasKey(SweepInput,"step-percent") else False
        if stepPercent:
            step = stepPercent * minimum
        if not step:
            #there was no step, print error and quit
            print("Error, config file: performance-sweep but no step")
            sys.exit(1) 
        sweepRange = list(np.arange(minimum,maximum+step,step))
    else:
        sweepRange = myRange
    currentExperiments = len(ourInput.keys())
    #if there were no sweeps before  
    if currentExperiments == 0: 
        count = 1
        for i in sweepRange:
            ourInput["experiment_{count}".format(count=count)]={"performance-factor":i}
            count+=1
    #there were sweeps before
    else:
        tmpInput = ourInput.copy()
        count = 1
        # update the current experiments first
        for i in ourInput.keys():
            data = ourInput[i].copy()
            data["performance-factor"] = sweepRange[0]
            ourInput[i] = data
            count+=1
        for i in sweepRange:
            if not i == sweepRange[0]:  #skip the first, we already did it
                for j in tmpInput.keys():
                    data = tmpInput[j].copy()
                    data["performance-factor"] = i
                    ourInput["experiment_{count}".format(count=count)] = data
                    count+=1
