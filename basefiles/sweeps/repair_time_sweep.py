from sweeps.sweepFunctions import *
import numpy as np
import sys

def repairTimeSweep(SweepInput,ourInput,origInput):
    myRange = SweepInput["range"] if dictHasKey(SweepInput,"range") else False
    myFormula = SweepInput["formula"] if dictHasKey(SweepInput,"formula") else False
    
    #no range
    if type(myRange) == bool:
        minimum = SweepInput["min"]
        maximum = SweepInput["max"]
        step = SweepInput["step"] if dictHasKey(SweepInput,"step") else False
        stepPercent = SweepInput["step-percent"] if dictHasKey(SweepInput,"step-percent") else False
        if stepPercent:
            step = np.ceil(stepPercent * minimum).astype('int')
        if not step:
            #there was no step, print error and quit
            print("Error, config file: repairTime-sweep but no step")
            sys.exit(1) 
        if myFormula:
            formula_range = list(range(minimum,maximum+step,step))
            repairTimeRange = [eval(myFormula) for i in formula_range]
        else:
            repairTimeRange = list(range(minimum,maximum+step,step))
    #yes a range
    else:
        if myFormula:
            formula_range = myRange
            repairTimeRange = [eval(myFormula) for i in formula_range]
        else:
            repairTimeRange = myRange
    currentExperiments = len(ourInput.keys())
    #if there were no sweeps before  
    if currentExperiments == 0: 
        count = 1
        for i in repairTimeRange:
            ourInput["experiment_{count}".format(count=count)]={"repair-time":i}
            count+=1
    #there were sweeps before
    else:
        tmpInput = ourInput.copy()
        count = 1
        # update the current experiments first
        for i in ourInput.keys():
            data = ourInput[i].copy()
            data["repair-time"] = repairTimeRange[0]
            ourInput[i] = data
            count+=1
        for i in repairTimeRange:
            if not i == repairTimeRange[0]:  #skip the first, we already did it
                for j in tmpInput.keys():
                    data = tmpInput[j].copy()
                    data["repair-time"] = i
                    ourInput["experiment_{count}".format(count=count)] = data
                    count+=1

