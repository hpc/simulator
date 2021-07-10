PREPARE
--------
If you haven't yet, look over the file README_FILES.txt to see what each file does.
In particular, look over deploy.sh and generate_config.py


INSTALL
--------
cd /home/$USER
cp ./monte_carlo/deploy.sh /home/$USER/deploy.sh
./deploy.sh


gcc: 10.2.0
Kernel: 3.10.0-1160.6.1.el7.x86_64
python: 3.6.8





HOW TO RUN MONTE CARLO SIMULATION ON AC-CLUSTER
------------------------------------------------
cd monte_carlo
#if you don't have an experiments folder already
mkdir ../experiments
base=`pwd`

#Example: 
file1=./configs/configFileName.config
folder1=../experiments/configFileName


m#Actual for test (3 Runs of each simulation)
file1=./configs/MC_test.config
folder1=../experiments/MC_test

#Actual for the real thing
file1=./configs/MC.config
folder1=../experiments/MC

#THIS NEXT MANUAL SECTION CAN BE AUTOMATED WITH: [note: make sure you use double quotes or $base will not be substituted with it's value]
sed -i "s:TODO:$base/:g" ./configs/MC_test.config
sed -i "s:TODO:$base/:g" ./configs/MC.config


MANUAL: edit ./configs/MC.config
        for each "synthetic-workload", change "number-of-resources"
        and "duration-time" to have a path to wl[1-6].csv
        currently it is set for a made up path TODO/    TODO/wl[1-6].csv
        
        
        



sbatch -p usrc-nd02 -N1 -n1 -c1 --output=./myBatch.log --export=folder1=$folder1,file1=$file1,basefiles=$base ./myBatch

#make sure myBatch is running (ie there were no json problems in the config file )
squeue --format="%.18i %.9P %.8j %.8u %.8T %.10M %.9l %.6D %R %.120k"

#continue to squeue to check if jobs are completing and to tell when they have all been completed
squeue --format="%.18i %.9P %.8j %.8u %.8T %.10M %.9l %.6D %R %.120k" | tail -n 10

python3 aggregate_makespan.py -i $folder1

MANUAL:

analyze ../experiments/$folder1/total_makespan.csv
    * group by "exp" : so you will have wl[1-6]_24hr and wl[1-6]_13d
      * group by "job" in each "exp" grouping
            The job "experiment_1" will be the baseline
            The job "experiment_2" will be the 2x
            The job "experiment_3" will be the 5x
        * divide every "experiment_2"'s "makespan_sec" by "experiment_1"'s "makespan_sec"
        * divide every "experiment_3"'s "makespan_sec" by "experiment_1"'s "makespan_sec"


        
        
INFO ON HOW TO CHANGE CONFIG FILES
------------------------------------

python3 generate_config.py --config-info [ general | sweeps |
                                           node-sweep | SMTBF-sweep | checkpoint-sweep | checkpointError-sweep | performance-sweep |
                                           grizzly-workload | synthetic-workload |
                                           input-options | output ]
