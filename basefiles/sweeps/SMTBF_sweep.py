from sweeps.sweepFunctions import *
import numpy as np
import sys
 
def SMTBFSweep(SMTBFSweepInput,ourInput,origInput):
    myRange = SMTBFSweepInput["range"] if dictHasKey(SMTBFSweepInput,"range") else False
    myStickyRange=SMTBFSweepInput["sticky-range"] if dictHasKey(SMTBFSweepInput,"sticky-range") else False
    sticky=False if type(myStickyRange) == bool else True
    myFormula = SMTBFSweepInput["formula"] if dictHasKey(SMTBFSweepInput,"formula") else False
    fixedToNode = SMTBFSweepInput["compute-SMTBF-from-NMTBF"] if dictHasKey(SMTBFSweepInput,"compute-SMTBF-from-NMTBF") else False
    if type(myRange) == bool and type(myStickyRange) == bool:
        #ok so we are going to have a min,max,step
        minimum = float(SMTBFSweepInput["min"])
        maximum = float(SMTBFSweepInput["max"])
        step = float(SMTBFSweepInput["step"])
        if myFormula:
            #ok so we have a formula
            formula_range = list(np.arange(minimum,maximum+step,step))
            SMTBFRange = [eval(myFormula) for i in formula_range]
        else:
            SMTBFRange = list(np.arange(minimum,maximum+step,step))
    elif myFormula:
        if sticky:
            formula_range = myStickyRange
        else:
            formula_range = myRange
        SMTBFRange = [eval(myFormula) for i in formula_range]
    else:
        if sticky:
            SMTBFRange = myStickyRange
        else:
            SMTBFRange = myRange
        
    currentExperiments = len(ourInput.keys())
    if sticky and not(len(SMTBFRange) == currentExperiments):
        print("chose sticky-range for SMTBF but length of sticky-range does not match length of currentExperiments\n"+"SMTBFRange: "+str(len(SMTBFRange))
              +"   currentExperiments: "+ str(currentExperiments))
        raise ValueError("chose sticky-range for SMTBF but length of sticky-range does not match length of currentExperiments\n"+"SMTBFRange: "+str(len(SMTBFRange))
              +"   currentExperiments: "+ str(currentExperiments))
    #if there were no sweeps before.  Notice compute-SMTBF-from-NMTBF doesn't make sense if this is the case since there will be no nodes
    if currentExperiments == 0: 
        count = 1
        for i in SMTBFRange:
            ourInput["experiment_{count}".format(count=count)]={"SMTBF":i}
            count+=1
    #there were sweeps before
    else:
            
        tmpInput = ourInput.copy()
        count = 1
        # update the current experiments first, if sticky ONLY update the current experiments
        for i in ourInput.keys():
            data = ourInput[i]
            if fixedToNode == True:
                nodes = data["nodes"] if dictHasKey(data,"nodes") else False
                if type(nodes) == bool:
                    print("compute-SMTBF-from-NMTBF set but no nodes set")
                    sys.exit(1)
                if sticky:
                    data["SMTBF"] = SMTBFRange[count-1]/nodes
                else:
                    data["SMTBF"] = SMTBFRange[0]/nodes
            else:
                data["SMTBF"] = SMTBFRange[0]
            ourInput[i] = data
            count+=1
        if not sticky:
            for i in SMTBFRange:
                if not i == SMTBFRange[0]:  #skip the first, we already did it
                    for j in tmpInput.keys():
                        data = tmpInput[j].copy()
                        if fixedToNode == True:
                            nodes = data["nodes"] if dictHasKey(data,"nodes") else False
                            if type(nodes) == bool:
                                print("compute-SMTBF-from-NMTBF set but no nodes set")
                                sys.exit(1)
                            data["SMTBF"] = i/nodes
                        else:
                            data["SMTBF"] = i
                        ourInput["experiment_{count}".format(count=count)] = data
                        count+=1
