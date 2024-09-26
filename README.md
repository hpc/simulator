<!-- Required extensions:  codehilite,markdown.extensions.tables,pymdownx.magiclink,pymdownx.betterem,pymdownx.tilde,pymdownx.emoji,pymdownx.tasklist,pymdownx.superfences,pymdownx.saneheaders -->




<!-- ----------------------------------------------------------------  Intro --------------------------------------------- -->
<h1>Simulator</h1>
Copyright Notice
----------------
Copyright © 2024 Triad National Security, LLC.
Release Approved Under O#4697 - LANL-contributed enhancements to BatSim toolstack.

**'simulator'** is a job scheduling simulator.  It is all you need to clone to deploy our edited Batsim simulator.

Our edited Batsim and Batsched repos are located here:
- (https://github.com/hpc/batsim4)
- (https://github.com/hpc/batsched4)

Our work makes use of Inria's Batsim (https://batsim.readthedocs.io/) simulator.

We have added:

- a node fault model with repair times
- simulated checkpointing
- reservations
- some work with cores
- other useful additions
- real batsim checkpointing for longer simulations

These were added to 6 scheduling algorithms:

- fcfs_fast2
- easy_bf_fast2
- easy_bf_fast2_holdback
- easy_bf2
- easy_bf3
- conservative_bf $\space \space \space \space \space \space \mathbb{\color{darkred}\longleftarrow} \text{\color{darkred} reservations only work with this algorithm}$

In addition to this is also a framework for spinning up simulations and for post processing.

The initial deployment of our code is all handled by one deploy script.  The running of a simulation or simulations can all be done by writing a config file and running a single script.

Analysis of the simulation data is mostly up to you, but there are some helpful jupyter notebooks to faciliate this by looking at our code and modifying it for your needs.


<!-- ----------------------------------------------------------------  Table of Contents --------------------------------------------- -->
## Table of Contents

In order to keep this README tidy, we have used nested ```<details>``` that are closed.  This means the links to sub-sections will mostly not work in this Table of Contents.
- [Deployment](#deployment)
  - [Requirements](#requirements)
  - [Deploy Methods](#deploy-methods)
  - [Deploy: How To...](#deploy-how-to)
    - [Bare-Metal](#bare-metal)
    - [Docker](#docker)
    - [CharlieCloud with Internet](#charliecloud-with-internet)
    - [CharlieCloud without Internet](#charliecloud-without-internet)
- [Make Sure Everything Works](#make-sure-everything-works)
  - [Bare-Metal works](#bare-metal-works)
  - [Docker works](#docker-works)
  - [CharlieCloud works](#charliecloud-works)
- [How To Make a Config File - Crash Course](#how-to-make-a-config-file---crash-course)
  - [Basic Outline](#basic-outline)
  - [Sweeps](#sweeps)
    - [Explanation of Sweeps](#explanation-of-sweeps)
    - [Types of Sweep Functions](#types-of-sweep-functions)
    - [Current Sweeps Available - (Functions Allowed)](#current-sweeps-available---functions-allowed)
  - [Workloads](#workloads)
    - [grizzly-workload](#grizzly-workload)
    - [synthetic-workload](#synthetic-workload)
  - [Options](#options)
- [Run Batsim - Crash Course To myBatchTasks.sh](#run-batsim---crash-course-to-mybatchtaskssh)
  - [Batsim Environment - batsim\_environment.sh](#batsim-environment---batsim_environmentsh)
  - [myBatchTasks.sh](#mybatchtaskssh)
    - [File and Output Folder](#file-and-output-folder)
    - [Tasks Per Node](#tasks-per-node)
    - [Method](#method)
    - [Parallel-Method](#parallel-method)
    - [Socket-Start](#socket-start)
    - [WallClock-Limit](#wallclock-limit)
  - [Squeue Monitoring](#squeue-monitoring)
- [Further Reading](#further-reading)

<!-- ------------------------------------------------------------------------------------>
<!-- ------------------------------  Deployment -------------------------------------- -->
<!-- ------------------------------------------------------------------------------------>
***


# Deployment
Here you will learn how to deploy the simulator in an environment right for you.

<details><blockquote>

## Requirements

<details><blockquote>

Requirements (bare-metal and charliecloud):
- linux os
- gcc >= 8.0 (bare-metal needs c++17, charliecloud method may allow for previous versions)
- cmake >= 3.15.4  (maybe previous versions. at least 3.11)
- python == 3.6
- python3-venv
- pip3
- typical build system
    - make
    - build
    - git
    - patch (bare-metal)
    - libtool (if not installed, deployment can attempt to build and install)
    - pkg-config (if not installed, deployment can attempt to build and install)
    - build-essential (ubuntu package. named other things on other distros)
- bash shell

Requirements (docker method):
- linux os
- git
- docker running and working

</blockquote>
</details> <!-- end requirements -->

## Deploy Methods

<details><blockquote>

There are 4 methods of building and deploying our batsim applications.

- bare-metal
    - will compile and install everything you need into a directory
- docker
    - will compile and install everything you need into a docker container
    - currently there is no option of parallelism with this method
- charliecloud with internet
    - charliecloud is a container technology that works when docker is not an option (think clusters without docker)
    - will compile and install everything you need into a directory
- charliecloud without internet
    - charliecloud is a container technology that works when docker is not an option (think clusters without docker)
    - meant to be run where you have internet and then copy a folder (3.5GB) to the cluster without internet
        - will compile and install everything you need and will be packaged into a directory to be copied to your setup without internet, then you can attempt to unpackage it there.

</blockquote>
</details> <!-- end deploy methods -->


## Deploy: How To...

<details><blockquote>

All of the methods rely on running .../simulator/basefiles/deploy.sh.  One can run `deploy.sh --help` for complete usage info.

###  Bare-Metal

<details><blockquote>

1. obtain the code
2. change directories
3. deploy
```bash
git clone https://cswalke1:ekhr1Q_mL356zvCt_p2B@gitlab.newmexicoconsortium.org/lanl-ccu/simulator.git
cd simulator/basefiles
./deploy.sh -f bare-metal --prefix $(dirname $(pwd))
```
</blockquote>
</details> <!-- end bare-metal -->


### Docker

<details><blockquote>

1. obtain the code
2. change directories
3. deploy
```bash
git clone https://cswalke1:ekhr1Q_mL356zvCt_p2B@gitlab.newmexicoconsortium.org/lanl-ccu/simulator.git
cd simulator/basefiles
./deploy.sh -f docker
```
</blockquote>
</details> <!-- end docker -->

### CharlieCloud with Internet

<details><blockquote>

1. obtain the code
2. change directories
3. deploy
```bash
git clone https://cswalke1:ekhr1Q_mL356zvCt_p2B@gitlab.newmexicoconsortium.org/lanl-ccu/simulator.git
cd simulator/basefiles
./deploy.sh -f charliecloud
```
</blockquote>
</details> <!-- end charliecloud with internet -->

### CharlieCloud without Internet

<details><blockquote>

1. obtain the code
2. change directories
3. deploy package
4. change directories
5. scp folder
6. ssh to remote
7. change directories
8. unpackage
```bash
git clone https://cswalke1:ekhr1Q_mL356zvCt_p2B@gitlab.newmexicoconsortium.org/lanl-ccu/simulator.git
cd simulator/basefiles
./deploy.sh -f charliecloud --no-internet --package
cd ../../

#to be modified for your method of sending a folder to your remote location and logging in to your remote location
scp -r ./batsim_packaged user@remote.org:/home/USER/
ssh user@remote.org


cd /home/USER/batsim_packaged
./deploy.sh -f charliecloud --no-internet --un-package
```
</blockquote>
</details> <!-- end charliecloud without internet -->

</blockquote>
</details> <!-- end Deploy: How To... -->

</blockquote>
</details> <!-- end Deployment -->

<!-- ------------------------------------------------------------------------------------->
<!-- -----------------------  Make Sure Everything Works  ----------------------------- -->
<!-- ------------------------------------------------------------------------------------->
***


# Make Sure Everything Works
Here you will learn how to test that your deployment works

<details><blockquote>

You can make sure your particular deployment works by using our tests: `.../simulator/basefiles/tests/test_simulator.py`.


Keep in mind that SLURM tests assume the following:

- You are on a cluster running SLURM
- You have access to at least two (2) nodes, otherwise it's not much of a parallel test

 
## Bare-Metal works

<details><blockquote>

Read the following list of instructions and then perform the commands below it.

1. change directories (/path/to/simulator/basefiles)
2. edit batsim_environment.sh
3. source batsim_environment.sh
4. run test_simulator.py
5. make your selections:
   - choose local or slurm
   - choose bare-metal
   - choose either serial or parallel
     - serial will run 1 simulation per test, 1 at a time
     - parallel will give you options of how many simulations per test, and how many at a time per test
       - if local was chosen this will use background multiple processes
       - if slurm was chosen this will submit multiple jobs to SLURM  
6. wait for results
```bash
cd /path/to/simulator/basefiles
# edit ./batsim_environment.sh   
# make sure you point prefix to /path/to/simulator (don't include basefiles in the path)
source batsim_environment.sh
test_simulator.py
```


</blockquote>
</details> <!-- end bare-metal works -->
 
## Docker works

<details><blockquote>

Read the following list of instructions and then perform the commands below it.

1. create and run a container from your "simulator_compile" image
2. change directories (should already be in the correct directory)
3. edit basefiles/batsim_environment.sh 
4. source batsim_environment.sh
5. run test_simulator.py
6. make your selections:
   - choose local or slurm
   - choose docker
    - serial is the only option here, so the simulations will start immediately
7. wait for results

```bash
docker run -it --name sim_test simulator_compile:latest
inside docker> cd /home/sim/simulator/basefiles
inside docker> # edit ./batsim_environment.sh  # prefix should be /home/sim/simulator
inside docker> source batsim_environment.sh
inside docker> test_simulator.py
```

</blockquote>
</details> <!-- end docker works -->

## CharlieCloud works

<details><blockquote>

Read the following list of instructions and then perform the commands below it.

1. change directories (/path/to/simulator/basefiles)
2. edit batsim_environment.sh
3. source batsim_environment.sh
4. run test_simulator.py
5. make your selections:
   - choose local or slurm
   - choose charliecloud
   - choose either serial or parallel
     - serial will run 1 simulation per test, 1 at a time
     - parallel will give you options of how many simulations per test, and how many at a time per test
       - if local was chosen this will use background multiple processes
       - if slurm was chosen this will submit multiple jobs to SLURM  
6. wait for results
```bash
cd /path/to/simulator/basefiles
# edit ./batsim_environment.sh
# make sure you point prefix to /path/to/simulator (don't include basefiles in the path)
source batsim_environment.sh
test_simulator.py
```
</blockquote>
</details> <!-- end charliecloud works -->

</blockquote>
</details> <!-- end Make sure everything works -->


<!-- ---------------------------------------------------------------------------->
<!-- ---------------------  Crash Course Config ------------------------------ -->
<!-- ---------------------------------------------------------------------------->
***


# How To Make a Config File - Crash Course

In this crash course you will learn:

- Sweeps
- Workloads
- Options
  
<details><blockquote>

## Basic Outline

Here you will see what a basic outline of a config file is.  It will give you a good overview of what is included in one.

<details><blockquote>

```java
    The general format of a config file:
    
    {       <------------------------------------   Opening curly brace to be proper json
    
        "Name1":{       <------------------------   The name of an experiment comes first.  You can have multiple experiments
                                                    in one config file and each will end up in it's own folder under the --output folder.
                                                    Notice the opening and closing curly brace.  Make sure you put a comma after the closing
                                                    curly brace if you plan on having another experiment in the same config file

                #                           \       Json does not allow for comments (unfortunately).  You may still want comments in your config,  
                # python/shell comment       \      however.  You can use all of these types of comments and it will get removed before parsing.
                // c/c++ style comment        \     Be aware that it can get difficult to trace down a simple mistake in your config when many 
                /* c/c++ block style comment  /     comments are used due to the line numbers being off and generally more clutter in your config.
                    Comments are fun.        /      But comments can make things a lot clearer, too. 
                    This comment is too.    /       The original and a stripped version will be in your --output folder.
                */                
                
                
                "input":{    <-------------------   Always make sure you have an input and an output in your experiment
                
                    "node-sweep":{  <------------   It is MOST advisable to always start with a node-sweep.  All other sweeps can come after this one
                    
                    },
                    "synthetic-workload":{ <-----   Always include either a synthetic-workload or a grizzly-workload after your sweeps
                    
                    },
                    "option":value,        <-----   Include any options that will affect all of the jobs on the outside of any sweep or workload
                
                },    <--------------------------   Make sure you separate your input options with commas, but also remember to separate input
                                                    and output with a comma
                "output":{   <-------------------   Again, always make sure you have an input and output in your experiment
                
                    "option":value,   <----------   Output is a bit simpler than input.  Just make sure it is valid json
                    "option":value
                
                }
        
        
        },     <---------------------------------   This closes the experiment and here we have a comma because we included another experiment "Name2"
        "Name2":{
            "input":{
            
                ...  <--------------------------    Make sure you replace this ellipsis with at least:
                                                        * a node-sweep
                                                        * a workload
            },
            "output":{
            
                ...  <--------------------------    You should replace ellipsis with at least:
                                                        * "AAE":true | "makespan":true
                
            }    <------------------------------    Close output
        }  <------------------------------------    Close "Name2"          
    }  <----------------------------------------    Close json
    
```
</blockquote>
</details> <!-- end Basic Outline -->


## Sweeps

Learn what sweeps are and how to use them here.

<details><blockquote>

### Explanation of Sweeps

Here you will learn what Sweeps are.

<details><blockquote>

Sweeps are what we call it when we make a parameterized option.  When you start out you will have one job called 'experiment_1'.  If you add a sweep
that, say, sweeps over how many nodes your simulation will be using, then it will add to how many jobs you have.  

<br/>
Let's say you sweep from 1,000 nodes to 2,000 nodes with a step of 250.  Then you will have:

<br/>

- experiment_1: 1000 nodes
- experiment_2: 1250 nodes
- experiment_3: 1500 nodes
- experiment_4: 1750 nodes
- experiment_5: 2000 nodes


Now, the way sweeps work is that they loop over what is already there.  So if we add a failure sweep like SMTBF (**S**ystem **M**ean **T**ime **B**etween **F**ailure) after the node sweep, then it will take the first parameter of the SMTBF sweep and set it to the experiments 1-5 above.  But then it will copy those 5 experiments and set the failure parameter to the second parameter of the SMTBF sweep.

<br />
Let's say you sweep from a SMTBF of 20,000 seconds to 40,000 seconds with a step of 10,000.  Then you will have:

<br/>

- experiment_1: 1000 nodes  SMTBF: 20,000 sec
- experiment_2: 1250 nodes  SMTBF: 20,000 sec
- experiment_3: 1500 nodes  SMTBF: 20,000 sec
- experiment_4: 1750 nodes  SMTBF: 20,000 sec
- experiment_5: 2000 nodes  SMTBF: 20,000 sec
- experiment_6: 1000 nodes  SMTBF: 30,000 sec
- experiment_7: 1250 nodes  SMTBF: 30,000 sec
- experiment_8: 1500 nodes  SMTBF: 30,000 sec
- experiment_9: 1750 nodes  SMTBF: 30,000 sec
- experiment_10: 2000 nodes SMTBF: 30,000 sec
- experiment_11: 1000 nodes SMTBF: 40,000 sec
- experiment_12: 1250 nodes SMTBF: 40,000 sec
- experiment_13: 1500 nodes SMTBF: 40,000 sec
- experiment_14: 1750 nodes SMTBF: 40,000 sec
- experiment_15: 2000 nodes SMTBF: 40,000 sec

So I hope you can see how the experiments add up quickly.

- We started with 5 node parameters
- We added 3 SMTBF parameters
- This totals 5 * 3 = 15 jobs

If we add another sweep after the SMTBF sweep with 4 parameters that would be 5 * 3 * 4 = 60 jobs
</blockquote>
</details> <!-- end explanation of sweeps -->

### Types of Sweep Functions

Sweeps can parameterize in multiple ways.  Here are the methods used:

<details><blockquote>

- **(iMMS)** integer Min Max Step
  - start from the minimum to the maximum (inclusive) with a step (can be negative)
    ```java
    "min":0,
    "max":10,
    "step":2
    ```
- **(fMMS)** float Min Max Step
  - same as iMMS except you can use floating point numbers
- **(iR)** integer Range
  - simply a list of integers
    ```java
    "range":[10,20,30,80]
    ```
- **(fR)** float Range
  - same as iR except for floats
- **(iSR),(fSR)** integer Sticky Range and float Sticky Range
  - just like **iR** and **fR** except it requires the amount of values to equal the amount of jobs made from sweeps before it.  Instead of adding any more jobs, it sets the values contained in it to the jobs already there.
  - example:
    ```java
    "node-sweep":{"range":[1000,2000]},  //creates two jobs: experiment_1 and experiment_2
    "SMTBF-sweep":{"sticky-range":[20000,30000]} 
    // normally with "range" this would 
        //set 20,000 to experiment_1(1000 nodes) and experiment_2(2000 nodes) and 
        //set 30,000 to experiment_3(1000 nodes) and experiment_4(2000 nodes)
    //sticky-range, however, will
        //set 20,000 to experiment_1(1000 nodes)
        //set 30,000 to experiment_2(2000 nodes)
        //and that's all  
    //No experiment_3 or 4. It 'sticks' to what was there before.
    ```
- **(F)** formula
  - used in conjunction with iR, fR, iSR, fSR, iMMS and fMMS.  You can set a formula here with 'i' as your variable.  Each number in your min/max/step or range will be passed in as 'i' to your formula and the result will be your number.  Makes it easier to read.
  - Example:
    ```java
    "range":[2,3,4],
    "formula":"i*3600"  // will make 2 hours, 3 hours, 4 hours. easier than 7200 sec,10800 sec,14400 sec
    ```
    Example:
    ```java
    "min":1,
    "max":5,
    "step":1,
    "formula":"(10**i)/i"  //'i' can be used multiple times.  Any python statement can be evaluated here.
    ```
</blockquote>
</details> <!-- end types of sweep functions -->

### Current Sweeps Available - (Functions Allowed)

Here are the current sweeps available and the parameterization allowed.  All sweep names end in "-sweep"

<details><blockquote>

- **checkpointError** ***(fMMS,fR)***
  - Used in our Application Efficiency tests.  It adds/subtracts an error amount to optimal simulated checkpoint intervals
- **checkpoint** ***(iMMS,iR)***
  - The interval to use for simulated checkpoints.  This value is an integer, but can also be set to "optimal".
- **coreCount** ***(iMMS,iR)***
  - How many cores per node.  Currently only supported on fcfs_fast2, easy_bf_fast2, and easy_bf_fast2_holdback algorithms.
- **corePercent** ***(fMMS,fR)***
  - What percent of cores can be filled with 1 node jobs.  Currently only supported on fcfs_fast2, easy_bf_fast2, and easy_bf_fast2_holdback algorithms.
- **jobs** ***(iMMS,iR)***
  - How many jobs out of the workload to use.
- **MTTR** ***(fMMS,fR,F)***
  - **M**ean **T**ime **T**o **R**epair.  Used in conjunction with failures to set how long a repair lasts.  It will come up with random repair times each time a machine goes down based on an exponential distribution.
- **node** ***(fMMS,fR,F)***
  - How many nodes the cluster will have.
- **performance** ***(fMMS,fR)***
  - Will increase/decrease the length of all jobs by this factor (floating point)
- **queueDepth** ***(iMMS,iR)***
  - In conservative_bf algorithm, will only schedule this amount of queued jobs before stopping.  This will speed things up considerably.
- **repairTime** ***(iMMS,iR,F)***
  - Similar to MTTR, but, instead of a random MTTR, this will set a fixed repair time for the whole simulation.
- **reservation** (None - check docs)
  - This is used in conjunction with conservative_bf algorithm to simulate reservations.  There is a whole syntax to this, so one should look at the documentation for info on it.
- **sharePackingHoldback** ***(iMMS,iR)***
  - When using cores, this will holdback x amount of nodes for sharing jobs.  All other nodes will not share jobs.  Only used with easy_bf_fast2_holdback algorithm.
- **SMTBF** ***(fMMS,fR,fSR,F)***
  - **S**ystem **M**ean **T**ime **B**etween **F**ailures.  Used as the primary source of failures.  It will come up with random failure times with an exponential distribution, and will come up with a random machine to have the failure with a normal distribution.
  - has a compute-SMTBF-from-NMTBF option
    - Will treat the values generated from this sweep as NMTBF's (**N**ode **M**ean **T**ime **B**etween **F**ailure) and will compute the SMTBF from the amount of nodes for that experiment
- **submissionCompression** ***(iMMS,iR,F)***
  - will compress/expand the time between submissions by a factor.
  
</blockquote>
</details> <!-- end current sweeps avaialable -->
</blockquote>
</details> <!-- end Sweeps -->

## Workloads

Here you will learn about the mandatory workload keys in a config file.<br/>
The following keys will be explained:<br/>
- grizzly-workload
- synthetic-workload

<details><blockquote>

### grizzly-workload

A grizzly-workload is named based on a certain 'grizzly' cluster at Los Alamos National Lab.  It is a 1490 node cluster and a 2018 real workload was acquired from the months of January to November.<br/>  
As long as the file the workload comes from conforms to the same requirements the 2018 workload conforms to, then the grizzly-workload is simply a 'real' workload that has options specific for it.  Requirements for your own 'grizzly-workload' are laid out in `.../simulator/basefiles/docs/User/User_Doc_Manual.pdf`

<details><blockquote>

- ### **Required Options**
  - ***type***
    - the type of profile to use: 'parallel_homogeneous' or 'delay'. With 'parallel_homogenous' run-time of a job is actually in terms of computational work done: flops/second.  It just so happens that when ***machine-speed*** is set to 1 then it translates into time.  'delay' deals only with time. Though 'parallel_homogeneous' may seem more complicated, it is recommended since other options and algorithms may use this flops/second functionality, such as using cores.
  - ***machine-speed***
    - used with 'parallel_homogeneous'.  It is the amount of flops of computation done in 1 second.  We highly recommend you set this to 1.
  - ***input***
    - the 'grizzly' or 'grizzly-like' workload file you will use.  'sanitized_jobs.csv' is the 2018 workload file we use.  Can be an absolute path or the name of a file in `.../simulator/basefiles`
  - ***time***
    - the time interval you would like to use in the workload.  
      - example: '03-01-2018:04-01-2018' would do March 1 till April 1.
      - example: ':'  would do all of the file. From Jan to November in the 2018 file.
      - example: '06-01-2018:' or ':05-01-2018'  From June on or From start to May respectively.
- ### **Additional Options**
  - ***number-of-jobs***
    - once a time period is chosen with **time**, you may choose how many of those jobs you want with this.  Starts from the front of **time** with a positive number.  Starts from the back with a negative number.  Takes precedence over regular option ***number-of-jobs*** and the **jobs-sweep**, so it should not be set if using the **jobs-sweep**.
  - ***random-selection***
    - used with 'number-of-jobs', will randomize which jobs are chosen.
      - example: 20  will seed the randomness with 20, making it deterministic
      - example: -1 will seed with time, making it random
  - ***submission-time***
    - The time between submissions and randomness used.  If omitted, will use the actual submission time in the ***input*** file. If set to '0:fixed', all jobs will submit at time zero.
      - syntax: \<float\>:\<exp|fixed\>. will use \<float\> seconds as the mean time ('exp'onential) or the actual time (fixed)
      - syntax: \<float1\>:\<float2\>:unif. will use a uniform distribution between \<float1\> and \<float2\>
  - ***wallclock-limit***
    - the amount of time that a job is able to use. If omitted, will use the actual wallclock-limit from the ***input*** file. 
      - syntax: \<float\>|'\<int\>%' a percent will be based off of the runtime of the job.
      - syntax: \<string\> either 'min:max[:seed]' or 'min%:max%[:seed]'  where min:max are floats and min% and max% are '\<int\>%'.  These are random numbers from min to max and an optional seed
      - example: '98%:102%:10'  from 98% of runtime to 102% of runtime with a seed of 10
  - ***read-time***
    - The amount of time to read in from a simulated checkpoint if checkpointing is turned on.  Follows the same syntax as wallclock-limit.  Mandatory if using checkpointing, but can be set to 0.
  - ***dump-time***
    - The amount of time to write out a simulated checkpoint if checkpointing is turned on.  Follows the same syntax as wallclock-limit.  Mandatory if using checkpointing, but can be set to 0.
  - ***checkpoint-interval***
    - The amount of time between successive writes of a simulated checkpoint on a per job basis.  Follows the same syntax as wallclock-limit.  Not mandatory since a system-wide simulated checkpoint interval can be set.
  - ***resv***
    - Sets what reservation definition to use.  Only used if you are simulating reservations of time, and only used with conservative_bf algorithm.
  - ***force-creation***
    - Workloads go in a database and will be re-used if they have the right characteristics.  If you want to roll the dice again you should force the creation of a new workload.
  - ***seed***
    - A seed that can be used on all randomness of the workload creation.  Otherwise it will use time, making it random unless individual seed options are used.
  - ***index***
    - Will set the index for a workload.  Suppose you made a random workload and it was added to the database.  You then wanted to run the experiment again but wanted a different roll of the dice for randomness, you could choose ***force-creation*** or just give it another index.  The benefit of using an index is that you could come back to using the same workload as long as the other workload options remained the same.
- ### **Regular Options That Effect Workloads**
  - ***submission-compression***
    - will compress/expand the time between submission of jobs
      - syntax: '\<int\>%' . below 100% compresses, above 100% expands
  - ***reservations-*** and ***reservation-sweep***
    - will define a reservation.  If ***resv*** is set for the workload then this changes the workload.
  - ***workload-ids***
    - This option piggy-backs off the ***index*** idea.
      - Jobs and Runs 
        - If you want different options you make multiple jobs in the form of experiment_# folders.  
        - If those options make batsim use randomness and you want to do some statistics by running batsim multiple times you use 'runs' by setting ***avg-makespan*** in the 'output' section of your config.
      - Ids
        - In contrast, if you want to make multiple random **workloads** for statistics, then you use 'ids' which can also be used in tandem with 'runs', though this gets complicated and may not aggregate properly at the time of this writing.TODO.
    - syntax: '[\<comma seperated range of ids\>]', example: '[1,5,8,20]'  , yes this is a string
    - syntax: 'min;max;step', example: '5;20;1' 
  - ***number-of-jobs***
    - Although ***number-of-jobs*** in the workload section takes precedence, number-of-jobs can be set in the regular options as well.  This is purely for the benefit of the **jobs-sweep**.
</blockquote>
</details> <!-- end grizzly-workload -->

### synthetic-workload

A synthetic-workload is simply a completely, or almost completely, made up workload.  There are many random options to give you the workload you require.

The reason we say 'almost completely' made up, is that there are 6 files that characterize different types of workloads based on the grizzly cluster.  In fact 'wl2.csv' was made from the same distribution of jobs that is in a particular real grizzly workload.

Whether you use these files or not is completely up to you.  We give you the tools to make a workload that suits you in the following list of options.
<details><blockquote>

- ### **Required Options**
  - ***type***
    - the type of profile to use: 'parallel_homogeneous' or 'delay'. With 'parallel_homogenous' run-time of a job is actually in terms of computational work done: flops/second.  It just so happens that when ***machine-speed*** is set to 1 then it translates into time.  'delay' deals only with time. Though 'parallel_homogeneous' may seem more complicated, it is recommended since other options and algorithms may use this flops/second functionality, such as using cores.
  - ***machine-speed***
    - used with 'parallel_homogeneous'.  It is the amount of flops of computation done in 1 second.  We highly recommend you set this to 1.
  - ***number-of-jobs***
    - The total number of jobs to make
  - ***number-of-resources***
    - The number of resources that each job will use
      - syntax: '\<int\>:fixed'
        - all jobs will have a fixed \<int\> amount of resources
      - syntax: '\<int1\>:\<int2\>:unif'
        - jobs will have from \<int1\> to \<int2\> uniformally random number of resources
      - syntax: '\<float1\>:\<float2\>:norm'
        - jobs will have from \<float1\> to \<float2\> normally random number of resources
      - syntax: '\<str\>:\<int\>:csv'
        - Will come from csv file at \<str\>.  \<str\> can be an absolute path or a file in `.../simulator/basefiles`.  \<int\> is the position in each row that holds the number of resources in the file. 0 is the first column.
        - csv files included are from wl1.csv to wl6.csv. wl1.csv starts at all 1 node jobs, wl2.csv is mostly 1 node jobs but resembles grizzly workloads in the past. wl3.csv is medium sized all the way up to wl6.csv which is the entire 1490 cluster on every job.
  - ***duration-time***
    - The length of time each job will use to complete
      - syntax: '\<float\>:\<exp|fixed\>'
        - all jobs will have a fixed \<float\> amount of runtime or an exponentially random runtime with a \<float\> mean time.
      - syntax: '\<float1\>:\<float2\>:unif'
        - jobs will have from \<float1\> to \<float2\> uniformally random number of runtime
      - syntax: '\<float1\>:\<float2\>:norm'
        - jobs will have from \<float1\> to \<float2\> normally random number of runtime
      - syntax: '\<str1\>:\<int\>:\<str2\>:csv'
        - Will come from csv file at \<str1\>.  \<str1\> can be an absolute path or a file in `.../simulator/basefiles`.  \<int\> is the position in each row that holds the number of resources in the file. 0 is the first column.\<str2\> is the unit of time that this represents in the file, so 'h|m|s' for hours or minutes or seconds. 'h' should be used with the included files.
        - csv files included are from wl1.csv to wl6.csv. wl1.csv is all 24 hour jobs as their width is only 1 resource. wl2.csv is varied but resembles grizzly workloads in the past. wl3.csv is medium length all the way up to wl6.csv which is entirely 24 hour jobs.
  - ***submission-time***
    - The time between submissions and randomness used. If set to 0:fixed, all jobs will submit at time zero.
      - syntax: '\<float\>:\<exp|fixed\>'
        - all jobs will have a fixed \<float\> amount of time between submissions or an exponentially random time with a \<float\> mean time between submissions.
      - syntax: '\<float1\>:\<float2\>:unif'
        - jobs will have from \<float1\> to \<float2\> uniformally random number of time between submissions
      - syntax: '\<float1\>:\<float2\>:norm'
        - jobs will have from \<float1\> to \<float2\> normally random number of time between submissions
- ### **Additional Options**
  - ***wallclock-limit***
    - the amount of time that a job is able to use. If omitted, will use -1, where the value will not be used in Batsim. 
      - syntax: \<float\>|'\<int\>%' a percent will be based off of the runtime of the job.
      - syntax: \<string\> either 'min:max[:seed]' or 'min%:max%[:seed]'  where min:max are floats and min% and max% are '\<int\>%'.  These are random numbers from min to max and an optional seed
      - example: '98%:102%:10'  from 98% of runtime to 102% of runtime with a seed of 10
  - ***read-time***
    - The amount of time to read in from a simulated checkpoint if checkpointing is turned on.  Follows the same syntax as wallclock-limit.  Mandatory if using checkpointing, but can be set to 0.
  - ***dump-time***
    - The amount of time to write out a simulated checkpoint if checkpointing is turned on.  Follows the same syntax as wallclock-limit.  Mandatory if using checkpointing, but can be set to 0.
  - ***checkpoint-interval***
    - The amount of time between successive writes of a simulated checkpoint on a per job basis.  Follows the same syntax as wallclock-limit.  Not mandatory since a system-wide simulated checkpoint interval can be set.
  - ***resv***
    - Sets what reservation definition to use.  Only used if you are simulating reservations of time, and only used with conservative_bf algorithm.
  - ***force-creation***
    - Workloads go in a database and will be re-used if they have the right characteristics.  If you want to roll the dice again you should force the creation of a new workload.
  - ***seed***
    - A seed that can be used on all randomness of the workload creation.  Otherwise it will use time, making it random unless individual seed options are used.
  - ***index***
    - Will set the index for a workload.  Suppose you made a random workload and it was added to the database.  You then wanted to run the experiment again but wanted a different roll of the dice for randomness, you could choose ***force-creation*** or just give it another index.  The benefit of using an index is that you could come back to using the same workload as long as the other workload options remained the same.
- ### **Regular Options That Effect Workloads**
  - ***submission-compression***
    - will compress/expand the time between submission of jobs
      - syntax: '\<int\>%' . below 100% compresses, above 100% expands
  - ***reservations-*** and ***reservation-sweep***
    - will define a reservation.  If ***resv*** is set for the workload then this changes the workload.
  - ***workload-ids***
    - This option piggy-backs off the ***index*** idea.
      - Jobs and Runs 
        - If you want different options you make multiple jobs in the form of experiment_# folders.  
        - If those options make batsim use randomness and you want to do some statistics by running batsim multiple times you use 'runs' by setting ***avg-makespan*** in the 'output' section of your config.
      - Ids
        - In contrast, if you want to make multiple random **workloads** for statistics, then you use 'ids' which can also be used in tandem with 'runs', though this gets complicated and may not aggregate properly at the time of this writing.TODO.
    - syntax: '[\<comma seperated range of ids\>]', example: '[1,5,8,20]'  , yes this is a string
    - syntax: 'min;max;step', example: '5;20;1' 
  - ***number-of-jobs***
    - Although ***number-of-jobs*** in the workload section takes precedence, number-of-jobs can be set in the regular options as well.  This is purely for the benefit of the **jobs-sweep**.
</blockquote>
</details> <!-- end synthetic-workload -->
</blockquote>
</details> <!-- end workloads -->

## Options

All other available options are described here.

<details><blockquote>

- ### **Required Options**
  - ***batsched-policy***
    - Sets which scheduling algorithm to use.  Is mandatory.
      - options: fcfs_fast2 | easy_bf_fast2 | easy_bf_fast2_holdback | easy_bf2 | easy_bf3 | conservative_bf
      - algorithms discussed in User Docs
- ### **Options That Can Effect The Workload**
  - ***submission-compression***
    - will compress/expand the time between submission of jobs
      - syntax: '\<int\>%' . below 100% compresses, above 100% expands
  - ***reservations-*** and ***reservation-sweep***
    - will define a reservation.  If ***resv*** is set for the workload then this changes the workload. more info for these are located in the User Docs.
  - ***workload-ids***
    - This option piggy-backs off the ***index*** idea.
      - Jobs and Runs 
        - If you want different options you make multiple jobs in the form of experiment_# folders.  
        - If those options make batsim use randomness and you want to do some statistics by running batsim multiple times you use 'runs' by setting ***avg-makespan*** in the 'output' section of your config.
      - Ids
        - In contrast, if you want to make multiple random **workloads** for statistics, then you use 'ids' which can also be used in tandem with 'runs', though this gets complicated and may not aggregate properly at the time of this writing.TODO.
    - syntax: '[\<comma seperated range of ids\>]', example: '[1,5,8,20]'  , yes this is a string
    - syntax: 'min;max;step', example: '5;20;1' 
  - ***number-of-jobs***
    - Although ***number-of-jobs*** in the workload section takes precedence, number-of-jobs can be set in the regular options as well.  This is purely for the benefit of the **jobs-sweep**.
- ### **Logging Options**
  - KEEP IN MIND THESE CAN TAKE UP A LOT OF HARD DRIVE SPACE, not meant to be used on a large set of simulations
  - ***batsched-log***
    - sets the logging for batsched
      - options: silent|debug|quiet|info|CCU_INFO|CCU_DEBUG|CCU_DEBUG_FIN|CCU_DEBUG_ALL
      - more info on these are in the User Docs
  - ***batsim-log***
    - sets the logging for batsim
      - options: network-only|debug|quiet|CCU_INFO|CCU_DEBUG|CCU_DEBUG_FIN|CCU_DEBUG_ALL
      - more info on these are in the User Docs
  - ***log-b-log***
    - if set to true will log B_LOG files ( these would need to be added to the scheduler code )
    - more info on these are in the Development Docs
  - ***output-svg***
    - Whether to output the schedule with algorithms that use the schedule
      - options: none | all | short
        - 'all' will output a svg every time an output_svg is encountered ( basically every time the schedule changes ). ONLY USE FOR SMALL WORKLOADS due to slow-down and Hard Drive space.
        - 'short' will output a svg every time there is a short output_svg ( happens much less than 'all').  STILL ONLY USE FOR SMALLER WORKLOADS due to slow-down and Hard Drive space 
  - ***output-svg-method***
    - What method to output the schedule
      - options: svg | text | both
        - 'svg' will output the svg files
        - 'text' will only output the schedule in text form in the batsched-log which requires it to be on info or CCU_INFO
        - 'both' does svg files and text in the log
  - ***svg-output-start***
    - What output number to start at.  If you know 'when' you want to concentrate on, in terms of how many svg's have been output, then set this number and possibly also the ***svg-output-end***.
  - ***svg-output-end***
    - What output number to end at.  If you know 'when' you want to concentrate on, in terms of how many svg's have been output, then set this number and possibly also the ***svg-output-start***.
  - ***svg-frame-start***
    - What frame number to start at.  A frame number is incremented each time make_decisions is entered.
  - ***svg-frame-end***
    - What frame number to end at.  A frame number is incremented each time make_decisions is entered.
  - ***svg-time-start***
    - What simulated time to start outputting the schedule.
      - syntax: \<float\> , in seconds
  - ***svg-time-end***
    - What simulated time to end outputting the schedule. -1.0 to go to the end of the simulation, the default.
      - syntax: \<float\> , in seconds
  - ***turn-off-extra-info***
    - Extra info is output to a file called 'out_extra_info.csv'.  It outputs a new line each time a job is completed.  It consists of 'jobs completed','percent done','utilization', schedule metrics, 'utilization', and memory usage.
      - set to true to turn this off.  Turning off will render progress.sh useless but may speed things up and will reduce Hard Drive space.
- ### **Failure Options**
  - ***MTTR***
    - **M**ean **T**ime **T**o **R**epair. Used in conjunction with failures to set how long a repair lasts.  It will come up with random repair times each time a machine goes down based on an exponential distribution.
  - ***SMTBF***
    - **S**ystem **M**ean **T**ime **B**etween **F**ailures.  Used as the primary source of failures.  It will come up with random failure times with an exponential distribution, and will come up with a random machine to have the failure on with a normal distribution.
  - ***calculate-checkpointing***
    - If set to true, computes the optimal simulated checkpointing interval for each job based on read time and dump time and the failure rate
  - ***checkpoint-interval***
    - Sets the system-wide simulated checkpoint interval
      - syntax: \<float\>
  - ***checkpointError***
    - Used in conjunction with ***calculate-checkpointing***.  Will increase or decrease the computed optimal checkpoint by the factor given by checkpointError.
      - syntax: \<float\> , above 1.0 is an increase, below 1.0 is a decrease.
  - ***checkpointing-on***
    - if set to true, will turn simulated checkpointing on.  Mandatory to do simulated checkpointing.
  - ***fixed-failures***
    - sets failures to be every simulated \<float\> seconds.  Is very useful in debugging.
  - ***queue-policy***
    - What the policy for the queue is when dealing with a re-submitted job.  The options are: FCFS | ORIGINAL-FCFS
    - Usually the queue is FCFS based on the submit time. ORIGINAL-FCFS would put resubmitted jobs at the front of the queue based on their original submit time.
  - ***reject-jobs-after-nb-repairs***
    - When failures result in machines going down because of a repair time on them, some jobs may not be able to run at all until machines become available.  If there are only jobs in the queue that fall into this situation then a mode can be flipped to count how many times a repair is done before any job has executed.  Once a job is able to execute, the count is reset. This setting waits \<int\> number of repairs being done before it gives up and rejects the jobs that are left. '-1' means the jobs will never be rejected in this situation, the default.
      - syntax: \<int\>
  - ***repair-time***
    - Sets a system-wide repair time in seconds.
      - syntax: \<float\>
  - ***seed-failures***
    - Will seed any random generators for failures, otherwise time is used.
      - syntax: \<int\>
  - ***seed-failure-machine***
    - Will seed any random generators for determining which machine should get the failure, otherwise time is used.
      - syntax: \<int\>
  - ***seed-repair-times***
    - Will seed any random generators for repair time, otherwise time is used
      - syntax: \<int\>
- ### **Real Checkpointing Options**
  - ***checkpoint-batsim-interval***
    - Will set an interval to do real checkpoints
      - syntax: \<string\>
        - "(real|simulated)[:once]:days-HH:MM:SS[:keep]"
          - 'real' prepended will interpret the interval to be in real time
          - 'simulated' prepended will interpret the interval to be in simulated time 
          - optional :once will do one checkpoint and then stop doing any more checkpoints
          - optional :keep will set the amount of checkpoints to keep.  ***checkpoint-batsim-keep*** trumps this
  - ***checkpoint-batsim-keep***
    - How many checkpoints to keep
      - syntax: \<int\>
  - ***checkpoint-batsim-signal***
    - The signal number to use for signal driven checkpointing.
      - syntax: \<int\> , You will want to either use SIGUSR1(10), SIGUSR2 (12), or preferably real-time signals from 35-64
- ### **Speed/Core Options**
  - ***core-percent***
    - Sets the limit on how many cores from a node can be used
      - syntax: \<float\> 
  - ***core-count***
    - Sets the amount of cores each node will have in the platform file and turns on '--enable-compute-sharing'
      - syntax: \<int\>
  - ***share-packing***
    - If set to true, will pack single resource jobs onto one node until that node reaches ***core-percent*** * available cores
  - ***share-packing-holdback***
    - If set to true, will holdback a certain number of nodes for exclusive share-packing
  - ***speeds***
    - Will set the speed of the cluster in the platform file
      - syntax: \<string\> , flops per second
        - Where \<string\> is '\<int\>f'.  
        - One can use size prefixes in front of 'f': K(10^3),M(10^6),G(10^9),T(10^12),P(10^15),E(10^18)
      - syntax: \<string1\>,\<string2\>,...
        - The difference here is that a list of strings is given, one for each pstate you use.  pstates will be explained in both User and Developer Docs
- ### **ALL OTHER OPTIONS**
  - ***copy***
    - The amount of copies the ending workload will have, along with submission time optional options.  This can be used to double up a workload when you double up the amount of nodes the cluster has.  This operates at the Batsim level, and not during workload creation.
      ```
        'format: '<#copies>[:(+|-):#:(fixed|#:unif:(single|each-copy|all)[:<seed#>] ])'
        '    or  '<#copies>[:=:#(fixed|((exp|:#:unif)[:<seed#>]) ]'
        'So you can just do number of copies, or
        ''=':
        '   * you can copy and set the submission time of the copy as an exponential,uniform,or fixed amount with '=', or
        ''+|-':
        '   * you can add a submission time to add some jitter. This submission time is either added or subtracted with (+|-)
        '   * This time can be a fixed number followed by :fixed or uniform random number between 2 numbers
        '   * If random:
        '       * you need to specify the second number with :#:unif:
        '       * you need to specify:  'single','each-copy',or 'all'
        '       * 'single' random number, single random number for 'each-copy', or random number for 'all'
        '2 copies here means if there are 10 jobs to start with, there will be 20 total after the operation.
        ' Examples:
        '                       '2'    - 2 copies no alteration in submission times
        '             '2:=:100:exp'    - 2 copies with 1 having original submission times, 1 having exponential random with a mean rate of 100 seconds.
        '             '2:=:0:fixed'    - 2 copies with 1 having original submission times, 1 having fixed time of 0
        '       '2:=:20:40:unif:30'    - 2 copies with 1 having original submission times, 1 having uniform random between 20 and 40 seconds. Use 30 as seed.
        '            '2:+:10:fixed'    - 2 copies, add 10 seconds fixed jitter to submission times
        '            '2:-:10:fixed'    - 2 copies, subtract 10 seconds fixed jitter from submission times
        '    '2:+:5:10:unif:single'    - 2 copies, get one random number between 5 and 10 and add it to all copied submission times
        '    '3:+:5:10:unif:all:20'    - 3 copies, get random numbers between 5 and 10 for all jobs of all copies, add it to submission times
        '                                  and seed the random generator with 20
        ' '3:+:5:10:unif:each-copy'    - 3 copies, get one random number between 5 and 10 and add it to all submission times of first copy
        '                                  then get another random number between 5 and 10 and add it to all sub times of second copy
      ```
  - ***submission-time-after***
    - This dictates the time between submissions and what kind of randomness.  It happens AFTER the copy operation and after sorting the jobs based on submission time.  This operates at the Batsim level, and not during workload creation.
        ```
        'format: '<#:(fixed[:#])|(exp|#:unif)[:(#|s[:#]])'
        '   or   'shuffle[:#]'
        'It is applied after sorting the current workload by submit time and after applying the copy option
        'If zero is used for a float,combined with ":fixed" then all jobs will start at time zero.
        'If omitted, the original submission times will be used, be that grizzly produced or synthetically produced
        'exp:    This will be exponentially distributed, random values with mean time between submissions to be FLOAT.
        'fixed:  All jobs will have this time between them unless zero is used for a FLOAT.
        'unif:   This will be uniform, random values from min:max
        's:      Used after the random types (exp|fixed|unif) to specify you want the job's submit times shuffled after.
        'shuffle: Will simply shuffle around the submit times amongst the jobs.
        'a seed can be put on the end of the string to use for deterministic behavior
        'ex:
        '       '--submission-time-after "200.0:exp:s"'
        '       '--submission-time-after "100.0:fixed"'
        '       '--submission-time-after "0.0:fixed"'
        '       '--submission-time-after "0:200.0:unif"'
        '       '--submission-time-after "200.0:exp:10"'  <-- 10 is the seed
        '       '--submission-time-after "0:200.0:unif:20"' <-- 20 is the seed
        '       '--submission-time-after "shuffle:20" <-- 20 is the seed
        ```
  - ***submission-time-before***
    - This is the same as ***submission-time-after*** except it happens BEFORE the copy operation and before sorting the jobs based on submission time. Both ***submission-time-before*** and ***submission-time-after*** can be used or either can be used on their own.
  - ***performance-factor***
    - Will increase/decrease the length of all jobs by this factor (floating point).  This operates at the Batsim level and not during workload creation.
      - syntax: \<float\> , above 1.0 will increase, below 1.0 will decrease
  - ***queue-depth***
    - The amount of items in the queue that will be scheduled
      - only used in conservative_bf
      - A lower amount will improve performance of the scheduler and thus the simulation but changes scheduling decisions and, so, gives different results
      - (-1) sets it to all items being scheduled, the default
   - ***reservations-start***
      - Meant for monte-carlo with reservations, staggering their start time.  
        - syntax: \<string\> 
        - \<string\> is string in following format:
            ```
            '<order#>:<-|+><#seconds>'
            where order# is the order (starting at 0) in the reservation array as described in your config file
            where you (must) choose -(negative,behind) or +(positive,ahead)
            where you specify the amount of seconds forward or backward
            'example_1: --reservations-start '0:+5'
            start the reservations with order# 0, 5 seconds ahead
            'example_2: --reservations-start '1:-2000'
            start the reservations with order# 1, 2000 seconds behind
            'example_3: --reservations-start '0:+5 , 1:-2000'
            only one invocation of this flag is allowed but values for different
            order #s can be acheived with a comma. spaces are allowed for easier viewing.
            ```
  - ***test-suite***
    - If set to true, will assume the folder structure has an umbrella folder to it, where multiple configs were being used and so multiple base folders are used under the umbrella folder.
    - This affects where the "current_progress.log" file is kept.  
      - This file keeps track of which simulations are finished and which successfully output a post_out_jobs.csv file.  This helps the test-suite determine what simulations have finished and whether to go on to the next step or not.
      - If an umbrella folder is used then "current_progress.log" is located one folder up from its base folder.   Otherwise it is located in its base folder.
  


</blockquote>
</details> <!-- end Options -->
</blockquote>
</details> <!-- end How to make a config file -->

<!-- ---------------------------------------------------------------------------->
<!-- ---------------------  Crash Course Batsim ------------------------------ -->
<!-- ---------------------------------------------------------------------------->
***

# Run Batsim - Crash Course To myBatchTasks.sh

In this crash course you will learn the very basics of myBatchTasks.sh - the script to turn your config file into running simulations.

Topics include:
- Batsim Environment
- myBatchTasks.sh
- Squeue Monitoring


<details><blockquote>

## Batsim Environment - batsim_environment.sh

You always want to make sure you get into your batsim environment first.

<details><blockquote>

To get into your batsim environment:

```bash
cd /path/to/simulator/basefiles
# make sure prefix is set in batsim_environment.sh
source batsim_environment.sh
```

Once you are in your batsim environment you have a few tools to use:

   - **batEnv**
     - Tells you what batsim environment you are in (prefix).  This is helpful if you have multiple deployments.
   - **batVersion**
     - Tells you what version of simulator you are using.  If one has problems it would be helpful to include:
       - batsim version
       - batsched version
       - batVersion
   - **batExit**
     - gets you out of the batsim environment.  
       - changes your:
         -  PATH - removes some added paths
         -  LD_LIBRARY_PATH - removes some added paths
         -  deactivates your python environment
         -  removes the (batsim_env) from your prompt
   - **batFile**
     - makes it easier to select a file to pass to myBatchTasks.sh
       - displays your configs directory and allows you to choose the numbered config file to set as $file1 .
     - also helps you select a folder.
     - use `batFile --help` for full usage.
   - **batFolder**
     - makes it easier to select a folder.
     - use `batFolder --help` for full usage.
   - **bind_all**
     - will bind certain keys to certain functions while inside the command-line terminal.
       - very helpful bindings for the keyboard.  For instance: type `cd ` then continue to press `alt+y` and you will see the history of just your `cd` command.
     - use `bind-all --help` to view all bindings that are made.
   - **basefiles scripts**
     - ***myBatchTasks.sh***
       - the main script you will use.
       - use `myBatchTasks.sh --help` to view the full usage.
     - ***progress.sh***
       - a very helpful script to view the progress of running simulations.
       - use `progress.sh --help` to view the full usage.
     - ***aggregate_makespan.py***
       - will aggregate results after simulations are finished.
       - use `aggregate_makespan.py --help` to view the full usage.
  
</blockquote>
</details> <!-- end batsim environment -->

## myBatchTasks.sh

<details><blockquote>

You run our simulations using a script called myBatchTasks.sh <br />
For help:
```bash
myBatchTasks.sh --help
```
### File and Output Folder

- The most important info to give it is the config file and the output folder
- If you provide just the name of the config file or just the name of the output folder, it will assume you are using the default
'configs' folder and the default 'experiments' folder respectively.
- You may not have space on these locations (particularly the output folder) so you can pass absolute paths to these locations.
- With the output folder **Make Sure**:
    - if using default locations (no slashes), that that folder does not exist in simulator/experiments/
    - if using absolute locations, that the leaf of the output folder does not exist

### Tasks Per Node

- We used this property to limit how many simulations would run on a node and thus limit its memory usage
    - You will also want to use it to limit simulations to less than or equal to the amount of cores on your nodes

### Method

- Very important, this says how you deployed batsim.
    - default is bare-metal

### Parallel-Method

- sets the type of parallel method.  
    - I suggest keeping this as 'tasks', the default.

### Socket-Start

- Batsim uses sockets to communicate with its sister program 'batsched'
- You need to use a different socket for each simulation
- If you only run myBatchTasks.sh once and you leave it till all jobs complete you have nothing to worry about
    - If you spin up some more simulations after myBatchTasks.sh returns control to the user you will need to figure how many simulations you currently have running
    - The paper uses 611 simulations.  If you are running the paper.config and want to spin up more simulations of something else, then add like 1,000 to the socket-start
        - So your socket-start would then be 11000
        - You must do your own book-keeping of sockets used

### WallClock-Limit

- Self explanatory in the output of --help

</blockquote>
</details> <!-- end  myBatchTasks.sh  -->

<!-- ---------------------  Squeue Monitoring ------------------------------ -->


## Squeue Monitoring

<details><blockquote>

We use a certain format passed to squeue to see which simulations are still running.<br />
It is advised you do the same.  Add the following to your .bashrc :<br />
```bash
function squeue ()
{
    if [[ $1 == "-s" ]]
    then
        /usr/bin/squeue --format="%.18i %.9P %.8u %.10M %.9l %.9N %.120j" "$@"
    else
        /usr/bin/squeue --format="%.18i %.9P %.8j %.8u %.8T %.10M %.9l %.6D %R %.120k" "$@"
    fi
}
```

To see the 'sbatch jobs' use `squeue` <br />
To see the 'srun tasks' use `squeue -s`
</blockquote>
</details> <!-- end squeue monitoring-->
</blockquote>
</details> <!-- end run batsim - crash course to mybatchtasks.sh -->

<!-- -------------------------------------------------------------------------------->
<!-- --------------------------   Further Reading -------------------------------- -->
<!-- -------------------------------------------------------------------------------->
***



# Further Reading

If you would like to run other experiments, feel free to learn about our simulator and all of the ins and outs of it.  We include Walkthroughs for guided tutorials, and Manuals to serve as a more complete reference.

While we hope that this simulator suits your needs, it is inevitable that some may have uses that are not included.  We feel that our work can be expanded on somewhat quickly so we include Development docs as well.
- User Docs 
  - Walkthrough
    - .../simulator/basefiles/docs/User/User_Doc_Walkthrough.pdf
  - Manual
    - .../simulator/basefiles/docs/User/User_Doc_Manual.pdf
- Development Docs
  - Walkthrough
    - .../simulator/basefiles/docs/Developer/Developer_Doc_Walkthrough.pdf
  - Manual
    - .../simulator/basefiles/docs/Developer/Developer_Doc_Manual.pdf














