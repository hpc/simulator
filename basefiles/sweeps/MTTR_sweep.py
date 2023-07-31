from sweeps.sweepFunctions import *
import numpy as np

def MTTRSweep(SweepInput,ourInput,origInput):
    sweepName="MTTR"
    myRange = SweepInput["range"] if dictHasKey(SweepInput,"range") else False
    myFormula = SweepInput["formula"] if dictHasKey(SweepInput,"formula") else False
    if type(myRange) == bool:
        #ok so we are going to have a min,max,step
        minimum = float(SweepInput["min"])
        maximum = float(SweepInput["max"])
        step = float(SweepInput["step"])
        if myFormula:
            #ok so we have a formula
            formula_range = list(np.arange(minimum,maximum+step,step))
            sweepRange = [int(eval(myFormula)) for i in formula_range]
        else:
            sweepRange = list(range(int(minimum),int(maximum+step),int(step)))
    elif myFormula:
        formula_range = myRange
        sweepRange = [int(eval(myFormula)) for i in formula_range]
    else:
        sweepRange = myRange
    currentExperiments = len(ourInput.keys())
    #if there were no sweeps before  
    if currentExperiments == 0: 
        count = 1
        for i in sweepRange:
            ourInput["experiment_{count}".format(count=count)]={sweepName:i}
            count+=1
    #there were sweeps before
    else:
        tmpInput = ourInput.copy()
        count = 1
        # update the current experiments first
        for i in ourInput.keys():
            data = ourInput[i].copy()
            data[sweepName] = sweepRange[0]
            ourInput[i] = data
            count+=1
        for i in sweepRange:
            if not i == sweepRange[0]:  #skip the first, we already did it
                for j in tmpInput.keys():
                    data = tmpInput[j].copy()
                    data[sweepName] = i
                    ourInput["experiment_{count}".format(count=count)] = data
                    count+=1
