import json
import pandas as pd
import re
import numpy as np
import functions


def dictHasKey(myDict,key):
    if key in myDict.keys():
        return True
    else:
        return False


def get_random_type(string):
    #match "random:" in group 0 then match 1-infinity lowercase characters in group 1 then make sure there is a space after it
    #then match everything else in group 2
    regEx=re.compile(r"(random[:])([a-z]+)[ ](.+)")
    match=regEx.match(string)
    if match is None:
        return None
    else:
        return match.groups()[1]
def get_min_max_interval(value,string):
    
    #match value=# or value=#,# or value=[#,#-#,#]
    regEx=re.compile(".*({value}=)(?:(?:(-1|[0-9]+)|([0-9]+)[,]([0-9]+))(?:[ ]+|$)|[\[]([0-9\- ]+)[\]](?:[ ]+|$)).*".format(value=value))
    match=regEx.match(string)
    #match=None, nothing matched   match=  0=value 1=#|-1 2,3 = #,#  4= #-# # # #-#
    if match is None:
        return None
    else:
        match=match.groups()
        return match
def compute_random(match):
    import intervalset as iset
    import sys
    #match=  0=value 1=# 2,3 = #,#  4= #-# # # #-#
    if not match[1]==None:
        #ok we have a single number
        return ("single",int(match[1]))
    if not match[2]==None:
        if match[2]==match[3] or match[2] > match[3]:
            print("Error in compute_random:  min and max equal each other or min is not less than max: min: %d  max: %d" % (match[2],match[3]))
            sys.exit(1)
        
        #ok we have a min,max
        return ("min_max",np.random.randint(low=match[2],high=int(match[3])+1,size=1)[0],int(match[2]),int(match[3]))
    if not match[4]==None:
        #ok we have an intervalset
        ourList=iset.from_intervalset_to_list(match[4])
        high=len(ourList)
        #ok we have a list now randomly choose one number from it
        ourPick = np.random.randint(low=0,high=high,size=1)[0]
        return ("interval",ourList[ourPick],ourList)
        
    
def parse_machines_json(machinesJson,nb_reservations):
    #machineJson should look like this:
    #    {
    #       "prefix":"a",                  <---required though at the moment does nothing.  This is the prefix of the machine (host)
    #       "machine-speed":1,             <---required if reservation type is parallel_homogeneous
    #       "total-resources":"0-1489",    <---required, the available resources.  used with random
    #       "interval":"2-5"               <---optional, either 'interval' | 'resources'.  Interval translates to "alloc" in job item in workload
    #       "resources":5                  <---optional, either 'interval' | 'resources'.  Resources translates to "res" in job item in workload
    #       "interval":"random:unif [options]" <---optional, using random on interval, below for options
    #           "random:unif res-number="  <--- 5 would be 5 machines in an interval    5,8 would be randomly 5-8 machines in an interval
    #           "random:unif different-res-numbers=" <---- 1 would be 1 choice out of 5-8, 2 would be two choices maybe 5 and 7.  1,2 would be random 1-2 different choices. 0 would be all choices
    #           "random:unif different-intervals="   <---- for each res number how many different intervals. when set to 0 makes each one different
    #
    #     }            
    #machine settings 
    import intervalset as iset
    import sys         
    machineInterval=machinesJson["interval"] if dictHasKey(machinesJson,"interval") else False
    machineResources=machinesJson["resources"] if dictHasKey(machinesJson,"resources") else False
    totalResources=machinesJson["total-resources"] if dictHasKey(machinesJson,"total-resources") else False
    ourMachines=iset.from_intervalset_to_list(totalResources)
    if machineInterval:
        #ok we have an interval, is it random?
        if machineInterval.find("random") == -1:
            #ok it is not random, return the amount of reservations we need
            return ([machineInterval]*nb_reservations,[iset.size_of_intervalset(machineInterval)]*nb_reservations)
        else:
            #ok it is random,what type of random are we talking about?
            randomType=get_random_type(machineInterval)
            if randomType == "unif":
                #ok we are talking about a uniform random set
                #what kind of resources are we looking at
                match=get_min_max_interval("different-res-numbers",machineInterval)
                diffR=1
                if not match==None:
                    diffR=compute_random(match)[1]
                match = get_min_max_interval("res-number",machineInterval)
                if match==None:
                    print("no res-number in random interval")
                    sys.exit(1)
                #resource_info 0=type 1=single random number 2=None,min,ourList 3=None,None,max
                resource_info = compute_random(match)
                resNumberChoices=[]
                if (resource_info[0]=="single"):
                    resNumberChoices=[resource_info[1]]
                    resNumberLength=1
                if (resource_info[0]=="min_max"):
                    minR=resource_info[2]
                    maxR=resource_info[3]
                    resNumberLength=maxR+1 - minR
                    if diffR==-1:
                        diffR=resNumberLength
                    if diffR > resNumberLength:
                        print("problem with interval.  you want %d different resource numbers\n"%diffR + \
                            "but you can only choose %d. interval: %s"%(resNumberLength,machineInterval))
                    resNumberChoices = list(np.random.choice(range(minR,maxR+1),size=diffR,replace=False))
                if (resource_info[0]=="interval"):
                    resNumberLength=len(resource_info[2])
                    if diffR==-1:
                        diffR=resNumberLength
                    if diffR > resNumberLength:
                        print("problem with interval.  you want %d different resource numbers\n"%diffR + \
                            "but you can only choose %d. interval: %s"%(resNumberLength,machineInterval))
                    resNumberChoices=list(np.random.choice(resource_info[2],size=diffR,replace=False))
            
                resNumbers=[]
                
                # ok for each resNumberChoice we want to know how many reservations of each choice we want
                # we divide the reservations up (mostly) evenly among the resource number choices
                for i in range(0,len(resNumberChoices)):
                    resNumbers.append(functions.blockSize(i,len(resNumberChoices),nb_reservations))
                    

                # ok now we know what amount of resources we want
                # we now need to choose WHICH resources we want
                # different-intervals tells us how many different choices of resources we want for each resource amount
                match = get_min_max_interval("different-intervals",machineInterval)
                diffI=1
                if not match==None:
                    diffI = compute_random(match)[1]
                                 
                
                #ok now we construct intervals
                intervals=[]
                resources=[]
                count=0
                for i in resNumberChoices:
                    #so we have a specific resNumberChoice
                    #get diffI choices of that specific resNumberChoice
                    choices=[]
                    diffINow = diffI
                    if diffI == -1:
                        diffINow = resNumbers[count]
                    for j in range(0,diffINow):
                        choices.append(list(np.random.choice(range(0,len(ourMachines)),size=i,replace=False)))
                    choiceNumbers=[]
                    for number in range(0,len(choices)):
                        choiceNumbers.append(functions.blockSize(number,len(choices),resNumbers[count]))

                    #translate choices into machines then into intervalset then add to our intervals the amount needed
                    count_choice=0
                    for choice in choices:
                        #ok we have the index numbers into ourMachines that we want
                        #translate it
                        translation=[ourMachines[idx] for idx in choice]
                        #now we have a translation: ex: [5,8,9,10,20]
                        #now we need an intervalset
                        intervalset=iset.from_list_to_intervalset(translation)
                        #we now would have something like "5 8-10 20"
                        #now find out out of the choiceNumbers[count_choice] how much is in each choice
                        intervals+=[intervalset]*choiceNumbers[count_choice]
                        resources+=[len(choice)]*choiceNumbers[count_choice]
                        count_choice+=1
                    count+=1
                if not len(intervals) == nb_reservations:
                    print("Error with machine intervals %s . length = %d but nb_reservations = %d" % (machineInterval,len(intervals),nb_reservations))
                    exit(1)
                return (intervals,resources)
    else:
        #ok we have resources not intervals
        #is it random?
        if isinstance(machineResources,int):
            resources=[machineResources]*nb_reservations
            return (resources,resources)
        #ok we have a string, make sure it's a random
        if machineResources.find("random") == -1:
            #ok it is not random, try to convert to int
            resources=[int(machineResources)]*nb_reservations
            return (resources,resources)
        else:
            #ok it is random, what type of random?
            randomType=get_random_type(machineResources)
            if randomType == "unif":
                #ok we are talking about a uniform random set
                #what kind of resources are we looking at
                match = get_min_max_interval("different-res-numbers",machineResources)
                diffR=compute_random(match)[1]
                match = get_min_max_interval("res-number",machineResources)
                resource_info = compute_random(match)
                resNumberChoices=[]
                if resource_info[0]=="single":
                    resNumberChoices=[resource_info[1]]
                    resNumberLength=1
                if resource_info[0]=="min_max":
                    minR=resource_info[2]
                    maxR=resource_info[3]
                    resNumberLength=maxR+1 - minR
                    if diffR==-1:
                        diffR=resNumberLength
                    if diffR > resNumberLength:
                        print("problem with interval.  you want %d different resource numbers\n"%diffR + \
                            "but you can only choose %d. interval: %s"%(resNumberLength,machineInterval))
                    resNumberChoices = list(np.random.choice(range(minR,maxR+1),size=diffR,replace=False))
                if resource_info[0]=="interval":
                    resNumberLength=len(resource_info[2])
                    if diffR==-1:
                        diffR=resNumberLength
                    if diffR > resNumberLength:
                        print("problem with interval.  you want %d different resource numbers\n"%diffR + \
                            "but you can only choose %d. interval: %s"%(resNumberLength,machineInterval))
                    resNumberChoices=list(np.random.choice(resource_info[2],size=diffR,replace=False))
                resNumbers=[]
                # ok for each resNumberChoice we want to know how many reservations of each choice we want
                # we divide the reservations up (mostly) evenly among the resource number choices
                resources=[]
                for i in range(0,len(resNumberChoices)):
                    nb_each = functions.blockSize(i,len(resNumberChoices),nb_reservations)
                    resources+=[resNumberChoices[i]]*nb_each                  
                if not len(resources) == nb_reservations:
                    print("Error with machine resources %s . length = %d but nb_reservations = %d" % (machineResources,len(resources),nb_reservations))
                    exit(1)
                return (resources,resources)


