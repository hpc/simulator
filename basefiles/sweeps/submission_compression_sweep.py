from sweeps.sweepFunctions import *
import numpy as np

def submissionCompressionSweep(SweepInput,ourInput,origInput):
    sweepName="submission-compression"
    myRange = SweepInput["range"] if dictHasKey(SweepInput,"range") else False
    myFormula = SweepInput["formula"] if dictHasKey(SweepInput,"formula") else False
    if type(myRange) == bool:
        #ok so we are going to have a min,max,step
        minimum = int(SweepInput["min"])
        maximum = int(SweepInput["max"])
        step = int(SweepInput["step"])
        if myFormula:
            #ok so we have a formula
            formula_range = list(range(minimum,maximum+step,step))
            sweepRange = [eval(myFormula) for i in formula_range]
        else:
            sweepRange = list(range(minimum,maximum+step,step))
    elif myFormula:
        formula_range = myRange
        sweepRange = [int(eval(myFormula)) for i in formula_range]
    else:
        sweepRange = [int(i) for i in myRange]
    #convert over to strings***************************************************************
    sweepRange = [str(i)+"%" for i in sweepRange]
    #**************************************************************************************
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