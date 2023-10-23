def changeInputFiles(startFromCheckpoint,base):
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
                        with open(input_config,'w') as IOFile:
                            json.dump(config,IOFile,indent=4)

def move_output_folder(nb_startFromCheckpoint,path,wrapper):
    import os
    old_folder = f"{path}/expe-out"
    new_folder = f"{path}/old_expe-out"
    os.system(f"{wrapper} mv {old_folder} {new_folder}")
    os.system(f"{wrapper} mkdir {old_folder}")
    os.system(f"{wrapper} cp -R {new_folder}/checkpoint_{nb_startFromCheckpoint} {old_folder}/start_from_checkpoint")
    os.system(f"{wrapper} cp -R {new_folder}/cmd {old_folder}/cmd")
    os.system(f"{wrapper} cp {old_folder}/start_from_checkpoint/out_jobs.csv {old_folder}/out_jobs.csv")


   