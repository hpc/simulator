def changeInputFiles(startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,base):
    import os
    import json
    experiments=[i for i in os.listdir(base) if os.path.isdir(base+"/"+i) and i!="heatmaps"]
    for exp in experiments:
        jobs = [i for i in os.listdir(base+"/"+exp+"/")]
        for job in jobs:
            ids = [i for i in os.listdir(base+"/"+exp+"/"+job) if os.path.isdir(base+"/"+exp+"/"+job+"/"+i)]
            for theId in ids:
                runs = [i for i in os.listdir(base+"/"+exp+"/"+job+"/"+theId) if os.path.isdir(base+"/"+exp+"/"+job + "/" + theId +"/"+ i)]
                for run in runs:
                    input_config = f"{base}/{exp}/{job}/{theId}/{run}/input/config.ini"
                    if os.path.exists(input_config):
                        with open(input_config,'r') as IOFile:
                            config = json.load(IOFile)
                            config["start-from-checkpoint"]=startFromCheckpoint
                            config["start-from-checkpoint-keep"]=startFromCheckpointKeep
                            config["start-from-frame"]=startFromFrame
                            config["discard-last-frame"]=discardLastFrame
                        with open(input_config,'w') as IOFile:
                            json.dump(config,IOFile,indent=4)

def move_output_folder(nb_startFromCheckpoint,startFromCheckpointKeep,startFromFrame,discardLastFrame,path,wrapper):
    import os
    old_folder = f"{path}/expe-out"
    new_folder = f"{path}/expe-out_1"
    
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
            os.system(f"rm -r {old_folder}")
        
            #undo frame-keep
            frames.sort()
            for i in frames:
                if i == 1:
                    os.system(f"mv {path}/expe-out_{1} {path}/expe-out")
                else:
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
            os.system(f"rm -r {path}/expe-out_{i}")
            frames.remove(i)
    for i in frames:
        os.system(f"mv {path}/expe-out_{i} {path}/expe-out{i+1}")
    if startFromFrame > 1 :
        if (len(frames) == 0) or (startFromFrame > (max(frames)+1)):
            import sys
            print(f"ERROR!!! --start-from-frame {startFromFrame}  does not exist!")
            sys.exit()
    frame_folder = f"{path}/expe-out_{startFromFrame}"
    os.system(f"mv {old_folder} {new_folder}")
    os.system(f"mkdir {old_folder}")
    os.system(f"cp -R {frame_folder}/checkpoint_{nb_startFromCheckpoint} {old_folder}/start_from_checkpoint")
    os.system(f"cp -R {frame_folder}/cmd {old_folder}/cmd")
    os.system(f"cp {old_folder}/start_from_checkpoint/out_jobs.csv {old_folder}/out_jobs.csv")


   