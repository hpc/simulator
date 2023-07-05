from sweeps.sweepFunctions import *
import functions
import numpy as np
import sys
from copy import deepcopy
import json
import re
TIME_KEYS = ["subdivisions-unit","time","start","submit","submit-before-start","repeat-every"]
RANGE_KEYS = ["subdivisions","type","prefix","machine-speed","total-resources","interval","count"]
STEP_KEYS = ["subdivisions","machine-speed","count"]
MACHINE_KEYS = ["prefix","machine-speed","total-resources","interval","resources"]
RESERVATION_ORDER = ["subdivisions","subdivisions-unit","type","machines","repeat-every","time","start","submit","submit-before-start","count"]
MACHINES_ORDER = ["prefix","machine-speed","total-resources","interval","resources"]

def determineNumChanges(sweeps):
    return getMyChanges(sweeps,number_only=True)

def getMyChanges(sweeps,changes=1,number_only=False):
    from copy import deepcopy
    myChanges={}
    multipliers={}
    highestValue = 0
    for key in sweeps.keys():

        values = []
        valueOfKey = sweeps[key]
        #if key starts with curly braces with a number ie '{3}'
        #then skip.   This is a multiplier affect and will be dealt with after normal ones
        match = re.search(r'[ ]*{[ ]*[-+]?[0-9]+[ ]*}',str(key))
        if match != None:
            #well we have a multiplier, this can now be stripped off the key
            firstPart = str(key)[:match.span()[0]]
            secondPart = str(key)[match.span()[1]+1:]
            key = firstPart + secondPart
            #save this key:value in a key:value
            #the key will be what number multiplier we are on
            potentialNewKey = str(match.group()).strip("{} ")
            if dictHasKey(multipliers,potentialNewKey):
                #ok we need to add to what is there
                multiplierKey = potentialNewKey
                multiplierDict = multipliers[multiplierKey]
                multiplierDict.update({key:valueOfKey})
                #now write it out to multipliers
                multipliers[multiplierKey]=deepcopy(multiplierDict)
            else:
                #ok it is a new multiplier key, add it
                newKey = potentialNewKey
                multipliers[newKey] = {key:valueOfKey}
            continue
        if key in STEP_KEYS:
            valueOfKey = valueOfKey.strip("[]")
            if not valueOfKey.find(";") == -1:
                #ok we found a min,max,step
                min,max,step = valueOfKey.split(";")
                values = list(range(int(min),int(max)+int(step),int(step)))
                if len(values) != changes:
                    print(f"Error: {key} not the correct amount of values.")
                    print(f"values length:{len(values)}.  Should be {changes}")
                    myDebug()
                    sys.exit()
        if (len(values) == 0) and (key in RANGE_KEYS):
            valueOfKey = valueOfKey.strip("[]")
            values = valueOfKey.split(",")
        if (len(values) == 0) and (key in TIME_KEYS):
            values = expandTotalTime(valueOfKey)
        numValues=len(values)
        if (not number_only):
            if len(values) != changes:
                if len(values) == 1:
                    values = values*changes
                else:
                    print(f"Error: {key} not the correct amount of values.")
                    print(f"values length:{len(values)}.  Should be {changes}")
                    myDebug()
                    sys.exit()
        else:
            highestValue = numValues if numValues>highestValue else highestValue
        myChanges.update({key:deepcopy(values)})
    if number_only:
        return highestValue
    else:
        return deepcopy(myChanges),deepcopy(multipliers)
    
def reservationSweep(SweepInput,ourInput,origInput):

    #first get the name of the reservation sweep applies to
    myName = SweepInput["name"] if dictHasKey(SweepInput,"name") else False
    if myName == False:
        print("Error no name in reservation sweep.  We don't know what reservation you want to sweep over.")
        myDebug()
        sys.exit()
    #get the reservation
    resv=deepcopy(origInput["reservations-%s"%myName])
    #now iterate over the reservation-array
    count = 0
    #allChanges is a gauge of how many changes are in resvTypes. Each resvType should have the same amount of changes
    allChanges = 0
    #countingChanges is the amount of changes total for this resvType
    countingChanges = 0
    allReservations = []
    for resvType in resv["reservations-array"]:
        #ok we have a type apply the corresponding SweepInput
        sweeps = SweepInput["reservations-array"][count]
        #changes are how many different experiments are going to result from the base sweep(non-multiplier)
        changes = determineNumChanges(sweeps)
        #myChanges are the dict of non-multiplier key:values pair where # values=changes
        #multipliers is a dict(key of multiplier #)  of non-parsed dicts ( [multiplier-key][key][non-parsed value] )
        myChanges,multipliers = getMyChanges(sweeps,changes)
       
              
        #now integrate the changes with what's there
        #TODO there are conflicting keys: submit-before-start or submit
        #TODO                             interval or resources
        #TODO          and optional keys: repeat-every
        for key in resvType.keys():
            if key == "machines":
                for machineKey in resvType["machines"].keys():
                    if machineKey in myChanges.keys():
                        continue
                    valueOfKey = resvType["machines"][machineKey]
                    values = [valueOfKey]*changes
                    myChanges.update({machineKey:deepcopy(values)})
            else:
                if key in myChanges.keys():
                    continue
                valueOfKey = resvType[key]
                values = [valueOfKey]*changes
                myChanges.update({key:deepcopy(values)})
        #myReservations is the list of experiments using resvType as a base and swept over
        #after this loop it holds only non-multiplier experiments
        myReservations=[]
        for i in range(0,changes,1):
            reservation = {}
            reservation["machines"]={}
            machines={}
            for key in myChanges.keys():
                if key in MACHINE_KEYS:
                    machines[key]=myChanges[key][i]
                else:
                    reservation[key] = myChanges[key][i]
                reservation["machines"]=functions.orderDict(machines,MACHINE_KEYS)
                reservation = functions.orderDict(reservation,RESERVATION_ORDER)
            myReservations.append(deepcopy(reservation))
        if len(multipliers) == 0:
            if allChanges == 0:
                allChanges = changes
            elif allChanges != changes:
                print(f"Error! This reservation type in reservation-sweep has an unequal amount of changes than previous types.")
                print(f"Previous changes: {allChanges}   Current changes: {changes}")
                myDebug()
                sys.exit()
        if len(multipliers) > 0:
            #countingChanges keeps track of all the changes for this resvType ( number of experiments )
            countingChanges = changes
            #ok we have multipliers
            #first take all the keys and sort them
            aListOfKeys = list(multipliers.keys())
            aListOfKeys.sort(key=functions.natural_keys)
            #ok they are sorted, now iterate
            neg_reservations = []
            pos_reservations = []
            for multiplierKey in aListOfKeys:
                #lets iterate through all the sweep keys for this multiplier
                multiplierDict = multipliers[multiplierKey]
                #changes is # of values for this multiplierKey
                changes = determineNumChanges(multiplierDict)
                # myChanges is the key:values dict where # values = changes
                myChanges=getMyChanges(multiplierDict,changes)[0]
                #are these normal multipliers, or are they non-multiplier multipliers?
                if (multiplierKey.find("-") == -1) and (multiplierKey.find("+") == -1):
                    #so we have the changes for a single multiplier.  Make reservations out of it
                    #based on each reservation we already added from non-multipliers.
                    #myReservations are all the reservations(experiments) for this resvType appended
                    holdingReservations = deepcopy(myReservations)
                    for holdingReservation in holdingReservations:
                        tmpChanges = deepcopy(myChanges)

                        
                        #tmpChanges is myChanges which is the key:values dict where # values = changes
                        #go through each key in the holdingReservation.  If it already exists in tmpChanges
                        #then skip it, the values were already made for that key.  If not, take what is in
                        #the holdingReservation and multiply it by # values (changes) and add that key to tmpChanges with those values
                        for key in holdingReservation.keys():
                            if key == "machines":
                                for machineKey in holdingReservation["machines"].keys():
                                    if machineKey in myChanges.keys():
                                        continue
                                    valueOfKey = holdingReservation["machines"][machineKey]
                                    values = [valueOfKey]*changes
                                    tmpChanges.update({machineKey:values})
                            else:
                                if key in tmpChanges.keys():
                                    continue
                                valueOfKey = holdingReservation[key]
                                values = [valueOfKey]*changes
                                tmpChanges.update({key:values})
                        for i in range(0,changes,1):
                            reservation = {}
                            reservation["machines"]={}
                            machines={}
                            for key in tmpChanges.keys():
                                if key in MACHINE_KEYS:
                                    machines[key] = tmpChanges[key][i]
                                else:
                                    reservation[key] = tmpChanges[key][i]
                                reservation["machines"] = functions.orderDict(machines,MACHINES_ORDER)
                                reservation = functions.orderDict(reservation,RESERVATION_ORDER)
                            myReservations.append(deepcopy(reservation))
                            
                    countingChanges= countingChanges + countingChanges*changes
                #ok the multiplier key is negative.  This is a set of reservations not multiplied by multipliers
                elif multiplierKey.find("-") != -1:
                    #populate the myChanges dict with what is already in the original reservation if not specified in this multiplier key
                    for key in resvType.keys():
                        if key == "machines":
                            for machineKey in resvType["machines"].keys():
                                if machineKey in myChanges.keys():
                                    continue
                                valueOfKey = resvType["machines"][machineKey]
                                values = [valueOfKey]*changes
                                myChanges.update({machineKey:deepcopy(values)})
                        else:
                            if key in myChanges.keys():
                                continue
                            valueOfKey = resvType[key]
                            values = [valueOfKey]*changes
                            myChanges.update({key:deepcopy(values)})
                    #ok now make reservations out of myChanges
                    key_reservations=[]
                    for i in range(0,changes,1):
                        reservation = {}
                        reservation["machines"]={}
                        machines={}
                        for key in myChanges.keys():
                            if key in MACHINE_KEYS:
                                machines[key]=myChanges[key][i]
                            else:
                                reservation[key] = myChanges[key][i]
                            reservation["machines"]=functions.orderDict(machines,MACHINE_KEYS)
                            reservation = functions.orderDict(reservation,RESERVATION_ORDER)
                        key_reservations.append(deepcopy(reservation))
                    #keep putting the reservations at the beginning (-1 will have a lower number experiment # than -5 as -5 will be processed first)
                    neg_reservations=deepcopy(key_reservations) + neg_reservations
                elif multiplierKey.find("+") != -1:
                    #populate the myChanges dict with what is already in the original reservation if not specified in this multiplier key
                    for key in resvType.keys():
                        if key == "machines":
                            for machineKey in resvType["machines"].keys():
                                if machineKey in myChanges.keys():
                                    continue
                                valueOfKey = resvType["machines"][machineKey]
                                values = [valueOfKey]*changes
                                myChanges.update({machineKey:deepcopy(values)})
                        else:
                            if key in myChanges.keys():
                                continue
                            valueOfKey = resvType[key]
                            values = [valueOfKey]*changes
                            myChanges.update({key:deepcopy(values)})
                    #ok now make reservations out of myChanges
                    key_reservations=[]
                    for i in range(0,changes,1):
                        reservation = {}
                        reservation["machines"]={}
                        machines={}
                        for key in myChanges.keys():
                            if key in MACHINE_KEYS:
                                machines[key]=myChanges[key][i]
                            else:
                                reservation[key] = myChanges[key][i]
                            reservation["machines"]=functions.orderDict(machines,MACHINE_KEYS)
                            reservation = functions.orderDict(reservation,RESERVATION_ORDER)
                        key_reservations.append(deepcopy(reservation))
                    #keep putting the reservations at the end (+1 will come before +5)
                    pos_reservations.extend(deepcopy(key_reservations))
                        
                        
            countingChanges+=len(neg_reservations)+len(pos_reservations)
            #I want to put negative reservations before the multiplied ones
            myReservations=deepcopy(neg_reservations)+myReservations+deepcopy(pos_reservations)
            # we are now done adding reservations of this type since we have gone through all the multiplier keys for this type     
            if allChanges == 0:
                allChanges = countingChanges
            elif allChanges != countingChanges:
                print(f"Error! This reservation type in reservation-sweep has an unequal amount of changes than previous types.")
                print(f"Previous changes: {allChanges}   Current changes: {countingChanges}")
                myDebug()
                sys.exit()
            
        #now add these new reservations to the list of allReservations.  allReservations[0] will be all of the reservations of type reservations-array[0]
        # allReservations[1] will be all of the reservations of type reservations-array[1]
        allReservations.append(deepcopy(myReservations))
    #allReservations[0..] holds lists of all the experiments
    #allReservations[0][0] holds experiment_xtra1 reservation Type 1
    #allReservations[1][0] holds experiment_xtra1 reservation Type 2
    #allReservations[0][1] holds experiment_xtra2 reservation Type 1
    #...

    #if any list in allReservations doesn't hold the amount of changes(experiments)
    #that the others have (dictated by allChanges) then increase it by allChanges
    #this assumes (correctly) that it either holds allChanges' size list or size 1
    
    for i in range(0,len(allReservations),1):
        if len(allReservations[i]) != allChanges:
            allReservations[i]=allReservations[i] * allChanges
    
    #now put together the experiments
    allReservationsJson = []
    for i in range(0,allChanges,1):
        reservationJson = json.loads(json.dumps({}))
        reservationJson["reservations-array"]=[ deepcopy(resvType[i]) for resvType in allReservations]
        allReservationsJson.append(deepcopy(reservationJson))

            
    #we can start adding the reservations to what is already there
        
    currentExperiments = len(ourInput.keys())
    #if there were no sweeps before
    # really this is a formality, there should better be sweeps before (like nodes!) 
    if currentExperiments == 0: 
        for i in range(0,allChanges,1):
            ourInput["experiment_{count}".format(count=i+1)]={"resv":allReservationsJson[i]}
    #there were sweeps before -- definitely the more likely scenario
    else:
        #first make a copy so we know what the original was
        #we are editing ourInput
        tmpInput = deepcopy(ourInput)
        count = 1
        numOrigKeys = currentExperiments
        deletedTmpInput = False
        skipAlreadyThere = False
        # update the current experiments first
        # we will update them with just the first new reservationJson
        # then after that we will add new experiments starting with the second new reservationJson
        # so iterate over the keys(experiments) in ourInput
        
        for ikey in ourInput.keys():
            data = deepcopy(ourInput[ikey])
            #about to set the resv to this experiment
            #however, first check that it doesn't already have resv
            #if it does then we are talking about a 2nd,3rd... reservation-sweep
            if dictHasKey(data,"resv-sweep-number"):
                #we delete tmpInput because this isn't the first time we are seeing a reservation-sweep
                #that means tmpInput already has reservations associated with it
                # we will update tmpInput to include only the original experiments, before we added ANY
                # reservations, then we will add updated versions of these original experiments WITH our new
                # reservations generated from this particular reservation-sweep
                

                # suppose we did a node sweep: 1,2,3
                # ourInput: 3 sims
                #  n1
                #  n2
                #  n3
                # reservation-sweep 1 had 2 changes
                # ourInput: now 6 sims
                # n1 resv1    n1  resv2
                # n2 resv1    n2  resv2
                # n3 resv1    n3  resv2
                #
                # This would be the current state of ourInput and would transfer to tmpInput since we copy it above
                # What we mean to do with a second reservation-sweep is just apply the changes as if applied to the original
                # 3 node sweep
                # reservation-sweep 2 had 3 changes
                # ourInput: now 15 sims
                # n1 resv1    n1  resv2     n1 resv3    n1 resv4    n1 resv5
                # n2 resv1    n2  resv2     n2 resv3    n2 resv4    n2 resv5
                # n3 resv1    n3  resv2     n3 resv3    n3 resv4    n3 resv5
                # however if we kept tmpInput as it was we would have this:
                # ourInput: now 24 sims   9+ than it should.  Notice resv3,resv4,resv5 are repeated.  No extra knowledge will come of it
                # n1 resv1    n1  resv2     n1 resv3    n1 resv3    n1 resv4    n1 resv4    n1 resv5    n1  resv5
                # n2 resv1    n2  resv2     n2 resv3    n2 resv3    n2 resv4    n2 resv4    n2 resv5    n2  resv5
                # n3 resv1    n3  resv2     n3 resv3    n3 resv3    n3 resv4    n3 resv4    n3 resv5    n3  resv5

                # We keep a record of the original ourInput by first storing the current number of experiments
                # subsequently we store the amount of changes made, this isn't used yet
                # So we get the amount of original sims from ourList[0] and only include the sim in tmpInput
                # if the current experiment number is less than or equal to it
                # 
                # we don't add any of these reservations to the original, that would delete what was already there
                # so we change the starting point when iterating allReservationsJson to include the  first reservationJson
                # 

                if deletedTmpInput == False:
                    tmpInput = {}
                    deletedTmpInput = True
                
                ourList = deepcopy(data["resv-sweep-number"])
                numExperimentsToAddPerResvJson = ourList[0]
                currentExpNum = int(str(ikey).strip("experiment_"))
                if currentExpNum <= numExperimentsToAddPerResvJson:
                    tmpInput.update({ikey:data})
                ourList.append(len(allReservationsJson))
                data["resv-sweep-number"]=deepcopy(ourList)
                
                skipAlreadyThere = True
                count+=1
                continue
            else:
                data["resv-sweep-number"]=deepcopy([numOrigKeys,len(allReservationsJson)])
            data["resv"] = json.dumps(allReservationsJson[0])
            ourInput[ikey] = data
            #this keeps track of what experiment number we are on
            count+=1
        start = 1
        if skipAlreadyThere:
            start = 0
        
        for i in range(start,len(allReservationsJson),1):
            # we skip the first, if we already did it
            # now iterate over the original "ourInput" and add our resv to it
                for jkey in tmpInput.keys():
                    data = deepcopy(tmpInput[jkey])
                    if dictHasKey(data,"resv-sweep-number"):
                        ourList = deepcopy(data["resv-sweep-number"])
                        ourList.append(len(allReservationsJson))
                        data["resv-sweep-number"]=deepcopy(ourList)
                    else:
                        data["resv-sweep-number"]=deepcopy([numOrigKeys,len(allReservationsJson)])
                    
                    data["resv"] = json.dumps(allReservationsJson[i])
                    ourInput["experiment_{count}".format(count=count)] = data
                    #again this keeps track of what experiment number we are on
                    count+=1

