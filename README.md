# simulator
Our work makes use of Inria's Batsim (https://batsim.readthedocs.io/) simulator. We have added a node fault model and simulated job checkpoint / restart in order to more easily explore the trade-offs between performance and reliability. This repo is associated with our IEEE HPEC 2021 submitted article entitled "Exploring the Tradeoff Between Reliability and Performance in HPC Systems." <br/>

Scripts are provided to apply patches to the original Batsim source and run experiments congruent with those presented in our article. They have been packaged here to be applied, built, and executed in a dockerized format for ease of use and replication of our experimental data presented in the HPEC article.  Those that wish to learn more about the native Batsim are encouraged to visit the Batsim homepage directly.

## Table of Contents
- [Build Docker](#build_docker)
- [Run The Docker](#run_docker)
- [Test The Docker](#test_docker)
  - [Config File](#config)
    - [Intro To Config](#intro_to_config)
  - [Run Test](#run_test)
  - [Basic Steps](#basic_steps)
- [Explanation Of total_makespan.csv](#total_makespan)
- [Steps To Run Simulations](#steps_to_run)
  - [How To Edit Config File](#edit_config)
  - [Example](#fig4_leftsub_wl4)
- [Monte Carlo](#monte_carlo_start)

## <a name="build_docker"></a> How to build the docker

clone this repo:<br/>
```git clone https://github.com/hpec-2021-ccu-lanl/simulator.git``` <br/>
enter directory:<br/>
```cd simulator```<br/>
build the docker and name the image "simulator": <br/>
```docker build . -t simulator```<br/>




## <a name="run_docker"></a>How to run the docker

create the docker container based off the "simulator" image and name it "batsim_docker":<br/>
```docker create --name batsim_docker -t simulator```<br/>
start the docker container: <br/>
```docker start batsim_docker```<br/>
start an interactive shell:<br/>
```docker exec -it batsim_docker /bin/bash```




## <a name="test_docker"></a>Test the batsim_docker

Before we test our docker, please bear with us on some confusing terminology:

This needs clarification. An "experiment", as far as the config file is concerned, is a json element that
has an input and an output.  You can make multiple experiments in one config file.  Below, the "experiment" is "test" and all data for that experiment will be in the folder "test".<br/>

 Each "job", as it relates to the config file, is one set of parameters used for a simulation.  For example, a simulation having a cluster with 1500 nodes vs a simulation having a cluster with 1600 nodes are two different "jobs".  Similarly two simulations both having 1500 nodes but differing on SMTBF are two different "jobs".  The confusion here is that "jobs" in this sense are titled "experiment_#" and so are their folder that comes under the "experiment" folder.<br />

 "Runs" are simulations in the same "experiment" that have the exact same parameters and so come under the same "job" and are used for averaging purposes.  To further complicate things, there are the "simulated jobs".  These are part of the workloads that the simulator is running.<br />

## <a name="config"></a>Ok, that is out of the way
Test the batsim_docker to see if it gives you the correct results.  This will make sure the docker is running properly, but will also give you a chance to see how the process
of running simulations goes.  We will use a config file "test_docker.config".<br/>
```
{  "test":{
            "input": {
                        "node-sweep":{
                                "range":[1490]
                        },
                        "SMTBF-sweep":{
                                "compute-SMTBF-from-NMTBF":true,
                                "formula":"128736000 * (1/i)",
                                "range":[1,8]
                        },
                        "checkpoint-sweep":{
                                "range":["optimal"]
                        },
                        "performance-sweep":{
                                "range":[1.0]
                        },
                        "checkpointing-on":true,
                        "synthetic-workload":{
                                "number-of-jobs":30000,
                                "number-of-resources":"/home/sim/basefiles/workload_types/wl2.csv:0:csv",
                                "duration-time":"/home/sim/basefiles/workload_types/wl2.csv:1:h:csv",
                                "submission-time":"0:fixed",
                                "wallclock-limit":-1,
                                "dump-time":"3%",
                                "read-time":"2%"
                        }
          },
          "output": {
                        "AAE":true,
                        "avg-makespan":1
          }
   }
}
```

### <a name="intro_to_config"></a>Just a real quick intro to this config file...
- We are sweeping over nodes, but really there is no sweep, as we used a fixed "range" and in that list of nodes there
is only one value [1490].  There are tools available to do a real sweep, but we won't get into that just yet.<br/><br/>
- We use a formula for (**S**)ystem (**M**)ean (**T**)ime (**B**)etween (**F**)ailure.  
  - 128736000 * 1/i where "i" is replaced with a "range": [1,8]
  - So we will have 128736000 / **1** and 128736000 / **8**
  - For clarification: 128,736,000 node seconds = **24 system hrs** * **3600seconds/hr** * **1490 nodes/system**
    - so this is a system failure rate of 1 failure every 24 hours for baseline ( "range" : [1] ) and for 8x worse ( "range" : [8] )<br/><br/>
- We let the simulator compute the optimal checkpointing for each job
- We set the speed of the system to 1.0 (normal speed) where higher is slower ( a 30% faster and 30% slower system would be 0.70 and 1.30 respectively )
- We give an option for all jobs, checkpointing-on.
- We set up a workload
- We tell it what kind of output we need
  - Average Application Efficiency
  - makespan with only 1 run   (replace "1" with "200" for 200 runs)
    - we did not pass the seed-failures option to all jobs.  This means our results will be deterministic.  Therefore, we only need 1 run.  Normally we want to take an average of at least 200 runs when it is not deterministic. However, we need to confirm exact numbers for our test so we will keep it deterministic by leaving the seed-failures option off.





### <a name="run_test"></a>Ok, let's run this test

1. you should already be in the /home/sim/basefiles directory.   If not, head there. `cd /home/sim/basefiles`
2. set two variables to make things easier:<br/>
    ```file1=./configs/test_docker.config```<br/>
    ```folder1=test_docker```
3. Now we get our workloads made, input/output folders made for each run, underlying config files made, and then the simulations begin.
    ```python3 run_simulation.py --config $file1 --output ~/experiments/$folder1```
  - since the docker is not a cluster and simulations run sequentially, there is a handy counter that is flushed to output before every simulation.  For example:
```
    Experiment 1/1
    Job 1/2
    Run 1/1

    ...

    Experiment 1/1
    Job 2/2
    Run 1/1
```
4. We have results but they need to be aggregated: ```python3 aggregate_makespan.py -i ~/experiments/$folder1```
  - After running this you should have a file called "total_makespan.csv" under the ~/experiments/$folder1 folder

5. Now to make determining whether we have correct results easier, run the following:<br />
  ```
  cat ~/experiments/$folder1/total_makespan.csv | \
  awk -F, BEGIN'{printf "\n"}''(NR>1)''{printf "%f\t%s,%s\n",$5,$7,$8}'END'{printf "\n"}'
  ```

  you should get
  ```

  4896980.836070  "56 days, 16:16:20"            <----baseline makespan (displayed as seconds, then days,hh:mm:ss)
  7861976.738434  "90 days, 23:52:56"            <----8x worse failures makespan (displayed as seconds, then days,hh:mm:ss)

  ```

If you wanted to know how much worse the makespan is for the worse failure rate, it's just a matter of taking the 8x worse makespan (use the seconds) and dividing by the baseline (use the seconds).

### <a name="basic_steps"></a>So that's basically it
That is all that is needed to run simulations with the docker.  You basically edit the config file, set the file1/folder1, run "run_simulation.py", aggregate the results, and do something with the aggregation. <br />

## <a name="total_makespan"></a>total_makespan.csv clarification
Let's make the total_makespan.csv clear.  I've put definitions for each field:
```
The first line is the header:
,nodes,SMTBF,NMTBF,makespan_sec,avg_tat,makespan_dhms,avg_tat_dhms,AAE,checkpointed_num,percent_checkpointed,checkpointing_on_num,checkpointing_on_percent,job,exp
```
starting with "nodes"<br/>
- **nodes**
  - That's easy, just the amount of nodes the system had for that job
- **SMTBF**
  - System Mean Time Between Failure for that job
- **NMTBF**
  - Node Mean Time Between Failure for that job.  This is easier to look at and use for grouping as it doesn't matter how many nodes the system had for that job
- **makespan_sec**
  - makespan in seconds
- **avg_tat**
  - average Turn Around Time in seconds
- **makespan_dhms**
  - makespan in days, hours:minutes:seconds format.  Keep in mind that there is a comma in this representation
    which may or may not mess things up for your comma separated values' file parsing
- **avg_tat_dhms**
  - similar to makespan_dhms, it is the Turn Around Time in days, hours:minutes:seconds format
- **AAE**
  - The Average-Average Application Efficiency of the job
- **checkpointed_num**
  - The average number of jobs that had to be restarted(maybe multiple times) and had checkpointed before failing(so they were able to be restarted by reading the checkpoint data)
- **percent_checkpointed**
  - Same as checkpointed_num except given as a percent
- **checkpointing_on_num**
  - If a global checkpointing interval is 4 hours but the individual job in the simulation was only 1 hour then no checkpointing time takes place.  Same situation can happen with "optimal" as it is dependent on dump time and not run time.  In this situation we call checkpointing "off" for that individual job.  This field is an average amount of jobs where the jobs were long enough to incorporate checkpointing and were so called "on".
- **checkpointing_on_percent**
  - same as checkpointing_on_num except given as a percent
- **number_of_jobs**
  - The amount of jobs in the workload for that experiment
- **utilization**
  - The average utilization of the simulated system over the simulation's makespan.
- **job**
  - This needs clarification. An "experiment", as far as the config file is concerned, is a json element that
  has an input and an output.  You can make multiple experiments in one config file. Each "job", as it relates to the config file, is one set of parameters used for a simulation.  For example, a simulation using 1500 nodes vs a simulation using 1600 nodes are two different "jobs".  Similarly two simulations both having 1500 nodes but differing on SMTBF are two different "jobs".  The confusion here is that "jobs" in this sense are titled "experiment_#" and so are their folder that comes under the "experiment" folder. "Runs" are simulations in the same "experiment" that have the exact same parameters and so come under the same "job" and are used for averaging purposes.  To further complicate things, there are the "simulated jobs".  These are part of the workloads that the simulator is running.
  This field "job" is how it relates to the config file and will be called "experiment_#"
- **exp**
  - This is the "experiment" that the job belongs to.  Read "job" above for clarification.






## <a name="steps_to_run"></a>How to run some simulations

1.  Start the docker container: `docker start batsim_docker`
2.  Start an interactive shell: `docker exec -it batsim_docker /bin/bash`
3.  Change directory to "basefiles": `cd /home/sim/basefiles`
4.  Choose a config file and optionally edit it (*below): `nano ./configs/figure4_left_wl4.config`
5.  Set the config file you wish to run:`file1=./configs/figure4_left_wl4.config`
6.  Set the output folder you wish the output to go to ( a **new** folder ): `folder1=NAME`
7.  Run the simulation: `python3 run_simulation.py --config $file1 --output ~/experiments/$folder1`
8.  Aggregate results if need be: `python3 aggregate_makespan.py -i ~/experiments/$folder1`
9.  Process the results in ~/experiments/$folder1/total_makespan.csv

### <a name="edit_config"></a>How To Edit Config File
\* Instructions for editing config files can be seen by running the following commands:
 - view general info on config files: `python3 generate_config.py  --config-info general`
 - view general info on sweeps: `python3 generate_config.py --config-info sweeps`
 - All --config-info options can be seen by running: `python3 generate_config.py --help`
    - Under `Required Options 1 -> --config-info <type>` you can see the various types of info that is offered
    - generate_config.py will not generate your config file for you.  It is called that because it takes a config file that you will need to write and generates the underlying config files the simulator needs.

### <a name="fig4_leftsub_wl4"></a>For example:
  - Run a modified Figure 4, left-hand subfigure for workload 4:
    - `file1=./configs/figure4_left_wl4.config`
    - `folder1=fig4_left_wl4`
    - `python3 run_simulation.py --config $file1 --output ~/experiments/$folder1`
      - This command took about 1.5 hours on my computer
    - `python3 aggregate_makespan.py -i ~/experiments/$folder1`
    - Now divide each makespan_sec in total_makespan.csv by the makespan_sec for the baseline (the first job, "experiment_1")
      You should get roughly what is in Figure 4, left-hand subfigure for workload 4. Keep in mind, this is only 10 runs.  The paper used 1500 runs.
      - The following will do these calculations for you:
        ```
        baseline=`cat ~/experiments/$folder1/total_makespan.csv | awk -F, '(NR>1)''{print $5}' | awk '(NR==1)''{print}'` && cat ~/experiments/$folder1/total_makespan.csv | awk -F, '(NR>2)''{print $5}' | awk -v baseline=$baseline BEGIN'{i=1}''{ printf "%f\tworse failures:%dx\n", $1/baseline,2^i;i=i+1}'
        ```
        This is what I get running these commands:
        ```
        1.015441        worse failures:2x
        1.049923        worse failures:4x
        1.100013        worse failures:8x
        1.188432        worse failures:16x
        1.328728        worse failures:32x
        ```

## <a name="monte_carlo_start"></a>Monte Carlo

We used a cluster of 13 nodes with 30 processing cores on each node in order to get our results.  This is mainly due to the fact
that we wanted a statistical average for our makespans, as they are based on random events.  In most simulations we did, we found the makespan to converge at
around 200 runs.  For added assurance we did 1500 runs for each datapoint in the paper.  With each run usually taking a couple minutes, we found datapoints at a rate
of about 1 every 10 minutes.  In order to sweep the 1,2,4,8,16,32 SMTBF it would take around an hour or two for each workload.  We were looking at around
8 or 10 hours for all 6 workloads for 13 day baseline, and longer but around the same for the 24 hour. (more errors equates to longer simulation time).<br/>

For this reason, you may want to consider a cluster for your tests.  Our cluster uses SLURM and we leverage it for parallelization.  These steps and instructions need to be understood so that you can adapt them to your linux distro and cluster situation.

## Table Of Contents
- [How To Run Monte Carlo Simulations](#how_to_run)
  - [Prepare](#prepare)
  - [Install](#install)
  - [How To Run A Simulation On Our AC-Cluster](#how_to_run_ac)
    - [Run Simulation (generic)](#run_sim)
    - [Actual Test Simulation (3 runs)](#run_3sim)
    - [Actual Simulation (1500 runs)](#run_1500sim)
      - [myBatch Running?](#myBatch)
      - [Completed?](#completed)
      - [Aggregate Results](#aggregate_ac)
      - [Analyze](#analyze_ac)
  - [How To Change Config Files](#change_config_ac)

## <a name="how_to_run"></a> How To Run Monte Carlo Simulations

### <a name="prepare"></a> Prepare

If you haven't yet, read over **simulator / monte_carlo / README_FILES.txt** to see what each file does.<br />
In particular, look over **deploy.sh** and **generate_config.py**<br/>
You will undoubtedly need to edit **deploy.sh** for your needs.
### <a name="install"></a> Install

Change Directory to user directory<br/>
`cd /home/$USER`<br/>
Copy deploy.sh into user directory<br/>
`cp ./monte_carlo/deploy.sh /home/$USER/deploy.sh`<br/>
Copy patches of batsim and batsched to Downloads<br/>
`cp ./monte_carlo/patch_batsim.patch ~/Downloads/patch_batsim.patch`<br/>
`cp ./monte_carlo/patch_batsched.patch ~/Downloads/patch_batsched.patch`<br/>
Run deploy.sh . Again, this will need to be edited first<br/>
`./deploy.sh`<br/>

- gcc: 10.2.0
- Kernel: 3.10.0-1160.6.1.el7.x86_64
- python: 3.6.8

### <a name="how_to_run_ac"></a> How to Run A Simulation On Our AC-Cluster
Change Directory to **simulator / monte_carlo** <br/>
`cd monte_carlo` <br/>
if you don't have an experiments folder already <br/>
`mkdir ~/experiments` <br/>
<a name="run_sim"></a> <h4>Generic Example:</h4>

`file1=./configs/configFileName.config` <br/>
Make sure the folder name is different each time <br/>
`folder1=~/experiments/configFileName` <br/>
``` base=`pwd` ```<br/>
```
sbatch -p usrc-nd02 -N1 -n1 -c1 --output=./myBatch.log \
--export=folder1=$folder1,file1=$file1,basefiles=$base \
 ./myBatch
```
<a name="run_3sim"></a> <h4>Actual Test Simulation (3 Runs of each simulation)</h4>

`file1=./configs/MC_test.config`<br/>
`folder1=~/experiments/MC_test`<br/>
``` base=`pwd` ```<br/>
Run this once.  It changes a path that is needed for the simulation workload:<br/>
`sed -i "s:TODO:$base/:g" ./configs/MC_test.config`<br/>
```
sbatch -p usrc-nd02 -N1 -n1 -c1 --output=./myBatch.log \
--export=folder1=$folder1,file1=$file1,basefiles=$base \
 ./myBatch
```
<a name="run_1500sim"></a> <h4>Actual Simulation (1500 Runs of each simulation)</h4>

`file1=./configs/MC.config`<br/>
`folder1=~/experiments/MC`<br/>
``` base=`pwd` ```<br/>
Run this once.  It changes a path that is needed for the simulation workload:<br/>
`sed -i "s:TODO:$base/:g" ./configs/MC.config`<br/>
```
sbatch -p usrc-nd02 -N1 -n1 -c1 --output=./myBatch.log \
--export=folder1=$folder1,file1=$file1,basefiles=$base \
 ./myBatch
```



<a name="myBatch"></a>**Make sure myBatch is running (ie there were no json problems in the config file )**<br/>
`squeue --format="%.18i %.9P %.8j %.8u %.8T %.10M %.9l %.6D %R %.120k"`<br/>

<a name="completed"></a>**Continue to squeue to check if jobs are completing and to tell when they have all been completed**<br/>
`squeue --format="%.18i %.9P %.8j %.8u %.8T %.10M %.9l %.6D %R %.120k" | tail -n 10`<br/>

<a name="aggregate_ac"></a>**Aggregate Results**<br/>
`python3 aggregate_makespan.py -i $folder1`<br/>

<a name="analyze_ac"></a>**Analyze ../experiments/$folder1/total_makespan.csv**<br/>

  - group by "exp" : so you will have wl[1-6]_24hr and wl[1-6]_13d
    - group by "job" in each "exp" grouping
      - The job "experiment_1" will be the baseline
      - The job "experiment_2" will be the 2x
      - The job "experiment_3" will be the 5x
    - divide every "experiment_2"'s "makespan_sec" by "experiment_1"'s "makespan_sec"
    - divide every "experiment_3"'s "makespan_sec" by "experiment_1"'s "makespan_sec"
    - dividing can be done with an `awk` command
      - First get the baseline by replacing **NR==1** by **NR==#** where **#** equals the line that is the baseline<br/>
        ```baseline=`cat ~/experiments/$folder1/total_makespan.csv | awk -F, '(NR==1)''{print $5}'` ```<br/>
      - Next do the division. Replace **NR==2** with **NR==#** where **#** equals the line that you are dividing by the baseline:<br/>
        ```
        cat ~/experiments/$folder1/total_makespan.csv | awk -F, -v baseline=$baseline '(NR==2)''{printf "%f",$5/baseline}'
        ```


### <a name="change_config_ac"></a> INFO ON HOW TO CHANGE CONFIG FILES

This is covered in the docker sections, but here it is again:<br/>
```
python3 generate_config.py --config-info [ general | sweeps |
                                            node-sweep | SMTBF-sweep | checkpoint-sweep | checkpointError-sweep | performance-sweep |
                                            grizzly-workload | synthetic-workload |
                                            input-options | output ]
```
