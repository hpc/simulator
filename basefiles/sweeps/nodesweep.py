
from sweeps.sweepFunctions import *
import numpy as np

def nodeSweep(nodeSweepInput,ourInput):
    myRange = nodeSweepInput["range"] if dictHasKey(nodeSweepInput,"range") else False
    myFormula = nodeSweepInput["formula"] if dictHasKey(nodeSweepInput,"formula") else False
    if type(myRange) == bool:
        #ok so we are going to have a min,max,step
        minimum = float(nodeSweepInput["min"])
        maximum = float(nodeSweepInput["max"])
        step = float(nodeSweepInput["step"])
        if myFormula:
            #ok so we have a formula
            formula_range = list(np.arange(minimum,maximum+step,step))
            nodeRange = [int(eval(myFormula)) for i in formula_range]
        else:
            nodeRange = list(range(int(minimum),int(maximum+step),int(step)))
    elif myFormula:
        formula_range = myRange
        nodeRange = [int(eval(myFormula)) for i in formula_range]
    else:
        nodeRange = myRange
    currentExperiments = len(ourInput.keys())
    #if there were no sweeps before  
    if currentExperiments == 0: 
        count = 1
        for i in nodeRange:
            ourInput["experiment_{count}".format(count=count)]={"nodes":i}
            count+=1
    #there were sweeps before
    else:
        tmpInput = ourInput.copy()
        count = 1
        # update the current experiments first
        for i in ourInput.keys():
            data = ourInput[i].copy()
            data["nodes"] = nodeRange[0]
            ourInput[i] = data
            count+=1
        for i in nodeRange:
            if not i == nodeRange[0]:  #skip the first, we already did it
                for j in tmpInput.keys():
                    data = tmpInput[j].copy()
                    data["nodes"] = i
                    ourInput["experiment_{count}".format(count=count)] = data
                    count+=1

