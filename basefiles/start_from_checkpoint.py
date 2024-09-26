def myPrint(prompt):
    print(prompt)
def changeInputFiles(testSuite,skipCompletedSims,startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,discardLogs,base,configFile,ignoreDoesNotExist):
    import os
    import json
    import functions
    import sys
    
    experiments=[i for i in os.listdir(base) if os.path.isdir(base+"/"+i) and i!="heatmaps"]
    for exp in experiments:
        if functions.dictHasKey(configFile[exp]["input"],"checkpoint-batsim-requeue"):
            requeue = configFile[exp]["input"]["checkpoint-batsim-requeue"]
        #if myBatchTasks was not passed discard-old-logs then check if it is in the config file
        had_discard_old_logs=False
        if (discardLogs == -1) and functions.dictHasKey(configFile[exp]["input"],"discard-old-logs"):
            had_discard_old_logs=True
            discardLogs = configFile[exp]["input"]["discard-old-logs"]
        print(f"changing input files for experiment: {exp} ...")
        jobs = [i for i in os.listdir(base+"/"+exp+"/")]
        jobs.sort(key=functions.natural_keys)
        total_jobs=len(jobs)
        for job in jobs:
            print(f"\t changing input files for job: {job}/experiment_{total_jobs}  ...")
            ids = [i for i in os.listdir(base+"/"+exp+"/"+job) if os.path.isdir(base+"/"+exp+"/"+job+"/"+i)]
            ids.sort(key=functions.natural_keys)
            for theId in ids:
                runs = [i for i in os.listdir(base+"/"+exp+"/"+job+"/"+theId) if os.path.isdir(base+"/"+exp+"/"+job + "/" + theId +"/"+ i)]
                runs.sort(key=functions.natural_keys)
                for run in runs:
                    input_config = f"{base}/{exp}/{job}/{theId}/{run}/input/config.ini"
                    try:
                        checkpoint_path = f"{base}/{exp}/{job}/{theId}/{run}/output"
                        if startFromFrame == 0:
                            checkpoint_path = f"{checkpoint_path}/expe-out/checkpoint_{startFromCheckpoint}"
                        else:
                            checkpoint_path = f"{checkpoint_path}/expe-out_{startFromFrame}/checkpoint_{startFromCheckpoint}"
                        
                        
                        if os.path.exists(input_config):
                            with open(input_config,'r') as IOFile:
                                config = json.load(IOFile)
                                if requeue == True:
                                    config["checkpoint-batsim-requeue"]=True
                                if functions.dictHasKey(config,"start-from-checkpoint-keep") and (startFromCheckpointKeep == -1):
                                    startFromCheckpointKeep = config["start-from-checkpoint-keep"]
                                elif startFromCheckpointKeep == -1:
                                    startFromCheckpointKeep = 1
                                #so if we are requeuing and we didn't enter discardLogs in myBatchTasks and we didn't put the option in the .config file
                                #then if there was a previous value, use it
                                #this means that if you don't enter discardLogs and you don't want the option and you had a previous value you need to add -1 in the .config file
                                if (requeue == True) and (discardLogs == -1) and (functions.dictHasKey(config,"discard-old-logs")) and (not had_discard_old_logs):
                                    discardLogs = config["discard-old-logs"]
                                config["start-from-checkpoint"]=startFromCheckpoint
                                config["start-from-checkpoint-keep"]=startFromCheckpointKeep
                                config["start-from-frame"]=startFromFrame
                                config["discard-last-frame"]=discardLastFrame
                                config["discard-old-logs"]=discardLogs
                                config["skip-completed-sims"]=skipCompletedSims
                                config["test-suite"]=testSuite

                            with open(input_config,'w') as IOFile:
                                json.dump(config,IOFile,indent=4)
                        
                        else:
                            print(f"ERROR: In start_from_checkpoint.py in changeInputFiles():  '{base}/{exp}/{job}/{theId}/{run}/input/config.ini' does not exist")
                            with open (f"{base}/config_state.log","w") as OutFile:
                                json.dump(json.loads("{ \"generate_config\":false }"),OutFile)
                            sys.exit(1)
                        if not os.path.exists(checkpoint_path) and ignoreDoesNotExist == False:
                            print(f"ERROR: In start_from_checkpoint.py in changeInputFiles():  '{checkpoint_path}' does not exist")
                            print(f"If this does not matter to you provide --ignore-does-not-exist to myBatchTasks.py")
                            with open (f"{base}/config_state.log","w") as OutFile:
                                json.dump(json.loads("{ \"generate_config\":false }"),OutFile)
                            sys.exit(1)
                    except:
                        print(f"ERROR:there was an exception in start_from_checkpoint.py in changeInputFiles() for {base}/{exp}/{job}/{theId}/{run}/input/config.ini")
                        sys.exit(1)
def changeInputFile(run,testSuite,skipCompletedSims,startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,base,ignoreDoesNotExist):
    import os
    import json
    import functions
    import sys
    
    input_config = f"{run}/input/config.ini"
    try:
        checkpoint_path = f"{run}/output"
        if startFromFrame == 0:
            checkpoint_path = f"{checkpoint_path}/expe-out/checkpoint_{startFromCheckpoint}"
        else:
            checkpoint_path = f"{checkpoint_path}/expe-out_{startFromFrame}/checkpoint_{startFromCheckpoint}"
        
        
        if os.path.exists(input_config):
            with open(input_config,'r') as IOFile:
                config = json.load(IOFile)
                config["start-from-checkpoint"]=startFromCheckpoint
                config["start-from-checkpoint-keep"]=startFromCheckpointKeep
                config["start-from-frame"]=startFromFrame
                config["discard-last-frame"]=discardLastFrame
                config["skip-completed-sims"]=skipCompletedSims
                config["test-suite"]=testSuite
            with open(input_config,'w') as IOFile:
                json.dump(config,IOFile,indent=4)
        
        else:
            print(f"ERROR: In start_from_checkpoint.py in changeInputFiles():  '{run}/input/config.ini' does not exist")
            with open (f"{base}/config_state.log","w") as OutFile:
                json.dump(json.loads("{ \"generate_config\":false }"),OutFile)
            sys.exit(1)
        if not os.path.exists(checkpoint_path) and ignoreDoesNotExist == False:
            print(f"ERROR: In start_from_checkpoint.py in changeInputFiles():  '{checkpoint_path}' does not exist")
            print(f"If this does not matter to you provide --ignore-does-not-exist to myBatchTasks.py")
            with open (f"{base}/config_state.log","w") as OutFile:
                json.dump(json.loads("{ \"generate_config\":false }"),OutFile)
            sys.exit(1)
    except:
        print(f"ERROR:there was an exception in start_from_checkpoint.py in changeInputFiles() for {base}/{exp}/{job}/{theId}/{run}/input/config.ini")
        sys.exit(1)

def move_output_folder(nb_startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,discardLogs,path,wrapper):
    import os
    import json
    import sys
    import functions
    
    input_config = f"{os.path.dirname(path)}/input/config.ini" #.../Run_#/input/config.ini
    old_folder = f"{path}/expe-out"  #.../Run_#/output/expe-out
    new_folder = f"{path}/expe-out_1"
    #only allow discard-last-frame to happen once, and also start-from-frame should only happen once
    if os.path.exists(input_config):
            with open(input_config,'r') as IOFile:
                config = json.load(IOFile)
                config["discard-last-frame"]=False
                config["start-from-frame"]=0
            with open(input_config,'w') as IOFile:
                json.dump(config,IOFile,indent=4)
        
    else:
        print(f"ERROR: In start_from_checkpoint.py in move_output_folder():  '{run}/input/config.ini' does not exist")
        with open (f"{base}/config_state.log","w") as OutFile:
            json.dump(json.loads("{ \"generate_config\":false }"),OutFile)
        sys.exit(1)
    
    if discardLastFrame:
        if startFromFrame == 0:
                startFromFrame =1
        frames=[]
        # get the frames
        for i in os.listdir(path):
            filename = str(os.path.basename(i))
            print(filename)
            if os.path.isdir(path+"/"+i) and (filename.find("expe-out_")!=-1):
                #ok we have a directory in path that is a frame, add it to our frames
                frames.append(int(filename[9:]))
        #only continue to delete the last frame if there are other frames
        if len(frames) > 0:
            print(f"Removing {old_folder}",flush=True)
            os.system(f"rm -r {old_folder}")
        
            #undo frame-keep
            frames.sort()
            for i in frames:
                if i == 1:
                    print(f"moving {path}/expe-out_{1} {path}/expe-out",flush=True)
                    os.system(f"mv {path}/expe-out_{1} {path}/expe-out")
                else:
                    print(f"moving {path}/expe-out_{i} {path}/expe-out_{i-1}",flush=True)
                    os.system(f"mv {path}/expe-out_{i} {path}/expe-out_{i-1}")
    else:
        startFromFrame +=1
        
    #now we will operate like discardLastFrame never happened     
    #first we will operate on keep
    frames=[]
    # get the frames
    for i in os.listdir(path):
        filename = str(os.path.basename(i))
        if os.path.isdir(path+"/"+i) and (filename.find("expe-out_")!=-1):
            #ok we have a directory in path that is a frame, add it to our frames
            frames.append(int(filename[9:]))
    frames.sort(reverse=True)
    for i in frames:
        if i>=startFromCheckpointKeep:
            print(f"152: Removing {path}/expe-out_{i}",flush=True)
            os.system(f"rm -r {path}/expe-out_{i}")
            frames.remove(i)
    for i in frames:
        print(f"moving {path}/expe-out_{i} {path}/expe-out_{i+1}",flush=True)
        os.system(f"mv {path}/expe-out_{i} {path}/expe-out_{i+1}")
    if startFromFrame > 1 :
        if (len(frames) == 0) or (startFromFrame > (max(frames)+1)):
            import sys
            print(f"ERROR!!! --start-from-frame {startFromFrame}  does not exist!")
            sys.exit(1)
    print(f"frame_folder: {path}/expe-out_{startFromFrame}",flush=True)
    frame_folder = f"{path}/expe-out_{startFromFrame}"
    print(f"moving {old_folder} {new_folder}",flush=True)
    os.system(f"mv {old_folder} {new_folder}")
    for i in os.listdir(path):
        filename = str(os.path.basename(i))
        if os.path.isdir(path+"/"+i) and (filename.find("expe-out_")!=-1):
            #ok we have a directory in path that is a frame, add it to our frames
            frames.append(int(filename[9:]))
    frames.sort(reverse=True)
    for i in frames:
        if (discardLogs != -1) and (i > discardLogs):
            #ok we need to remove the logs
            os.system(f"rm -r {path}/expe-out_{i}/log")
    os.system(f"mkdir {old_folder}")
    #first check that checkpoint # is valid
    if not os.path.exists(f"{frame_folder}/checkpoint_{nb_startFromCheckpoint}"):
        print(f"ERROR! {frame_folder}/checkpoint_{nb_startFromCheckpoint} does not exist!!!")
        sys.exit(1)
    with open(f"{frame_folder}/checkpoint_{nb_startFromCheckpoint}/workload.json","r") as InFile:
        workload=json.load(InFile)
        if len(workload["jobs"]) == 0:
            print(f"ERROR! {frame_folder}/checkpoint_{nb_startFromCheckpoint}/workload.json has empty jobs array")
            sys.exit(1)
    os.system(f"cp -R {frame_folder}/checkpoint_{nb_startFromCheckpoint} {old_folder}/start_from_checkpoint")
    os.system(f"cp -R {frame_folder}/cmd {old_folder}/cmd")
    os.system(f"cp {old_folder}/start_from_checkpoint/out_jobs.csv {old_folder}/out_jobs.csv")
    os.system(f"mkdir {old_folder}/log")
    os.system(f"mv {old_folder}/start_from_checkpoint/Soft_Errors.log {old_folder}/log/")
    os.system(f"mv {old_folder}/start_from_checkpoint/failures.csv {old_folder}/")
