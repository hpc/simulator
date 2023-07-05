<!-- Required extensions:  codehilite,markdown.extensions.tables,pymdownx.magiclink,pymdownx.betterem,pymdownx.tilde,pymdownx.emoji,pymdownx.tasklist,pymdownx.superfences,pymdownx.saneheaders -->




<!-- ----------------------------------------------------------------  Intro --------------------------------------------- -->
$\textbf{\Huge simulator}$ <br />

Our work makes use of Inria's Batsim (https://batsim.readthedocs.io/) simulator.

We have added:

- a node fault model with repair times
- checkpointing
- reservations
- some work with cores
- other useful additions

These were added to 4 scheduling algorithms:

- fcfs_fast2
- easy_bf_fast2
- easy_bf_fast2_holdback
- conservative_bf $\space \space \space \space \space \space \mathbb{\color{darkred}\longleftarrow} \text{\color{darkred} reservations only work with this algorithm}$

In addition to this is also a framework for spinning up simulations and for post processing.

Scripts are provided to apply patches to the original Batsim source and run experiments congruent with those presented in our article.  The initial deployment of our code is all handled by one deploy script.  The running of a simulation or simulations can all be done by writing a config file and running a single script.

Analysis of the simulation data is mostly up to you, but there are some helpful jupyter notebooks to faciliate this by looking at our code and modifying it for your needs.  However, scripts for the analysis of data obtained from running the example configs that were used in our article are provided.  These can be run as-is.


<!-- ----------------------------------------------------------------  Table of Contents --------------------------------------------- -->
## Table of Contents
- [Deployment](#deployment)
    - [Deploy Methods](#build_methods)
    - [Deploy: How To...](#deploy_how_to)
        - [Bare-Metal](#deploy_bare_metal)
        - [Docker](#deploy_docker)
        - [CharlieCloud with Internet](#deploy_charliecloud_with_internet)
        - [CharlieCloud without Internet](#deploy_charliecloud_without_internet)
- [Make Sure Everything Works](#run_tests_works)
    - [Bare-Metal works](#run_tests_works_bare_metal)
    - [Docker works](#run_tests_works_docker)
    - [CharlieCloud works](#run_tests_works_charliecloud)
- [Verifying Paper](#run_tests_verify)
    - [Crash Course to myBatchTasks.sh](#crash_course)
    - [Squeue Monitoring](#squeue)
    - [Verifcation Methods](#run_tests_verify_methods)
        - [Bare-Metal verification](#run_tests_verify_bare_metal)
            - [parallel](#run_tests_verify_bare_metal_parallel)
            - [serial](#run_tests_verify_bare_metal_serial)
        - [Docker verification](#run_tests_verify_docker)
            - [parallel](#run_tests_verify_docker_parallel)
            - [serial](#run_tests_verify_docker_serial)
        - [CharlieCloud verification](#run_tests_verify_charliecloud)
            - [parallel](#run_tests_verify_charliecloud_parallel)
            - [serial](#run_tests_verify_charliecloud_serial)
    - [Analysis](#analysis)
- [Further Reading](#further_reading)
    - [Config Files](#config_files)


<!-- ----------------------------------------------------------------  Deployment --------------------------------------------- -->
***


<a name="deployment"></a>
# Deployment

Requirements (bare-metal and charliecloud):
- linux os
- gcc >= 8.0 (bare-metal needs c++17, charliecloud method may allow for previous versions)
- cmake >= 3.15.4  (maybe previous versions)
- python >= 3.6
- pip3
- make
- build
- git
- patch (bare-metal)
- typical build system

Requirements (docker method):
- linux os
- git
- docker running and working

<a name="build_methods"></a>
## Deploy Methods
<details>
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
    - meant to be run where you have internet and copy folder (3.5GB) to cluster without internet
        - will compile and install everything you need and will be packaged into a directory to be copied to your setup without internet

</details>

<a name="deploy_how_to"></a> 
## Deploy: How To...

<a name="deploy_bare_metal"></a>
###  Bare-Metal

<details>

1. obtain the code
2. change directories
3. deploy
```
git clone https://github.com/HPCMASPA2023-GitHub/simulator.git
cd simulator/basefiles
./deploy.sh -f bare-metal --prefix $(dirname `pwd`)
```

</details>

<a name="deploy_docker"></a>
### Docker

<details>

1. obtain the code
2. change directories
3. deploy
```
git clone https://github.com/HPCMASPA2023-GitHub/simulator.git
cd simulator/basefiles
./deploy.sh -f docker
```

</details>

<a name="deploy_charliecloud_with_internet"></a> 
### CharlieCloud with Internet
<details>

1. obtain the code
2. change directories
3. deploy
```
git clone https://github.com/HPCMASPA2023-GitHub/simulator.git
cd simulator/basefiles
./deploy.sh -f charliecloud
```

</details>

<a name="deploy_charliecloud_without_internet"></a> 
### CharlieCloud without Internet

<details>

1. obtain the code
2. change directories
3. deploy package
4. change directories
5. scp folder
6. ssh to remote
7. change directories
8. unpackage
```
git clone https://github.com/HPCMASPA2023-GitHub/simulator.git
cd simulator/basefiles
./deploy.sh -f charliecloud --no-internet --package
cd ../../
scp -r ./batsim_packaged user@remote.org:/home/USER/
ssh user@remote.org
cd /home/USER/batsim_packaged
./deploy.sh -f charliecloud --no-internet --un-package
```

</details>




<!-- ----------------------------------------------------------------  Make Sure Everything Works --------------------------------------------- -->
***



<a name="run_tests_works"></a> 
# Make Sure Everything Works

You can make sure your particular deployment works by looking at the section of your deployment method
and running the commands contained there.

Keep in mind that parallel tests assume the following:

- You are on a cluster running SLURM
- You have access to at least two (2) nodes


<a name="run_tests_works_bare_metal"></a> 
## Bare-Metal works

<details>

1. change directories
2. edit basefiles/batsim_environment.sh
3. run test_serial script
4. view result
5. run test_parallel script
6. view result
```
cd /path/to/simulator/basefiles
# edit ./batsim_environment.sh   
# make sure you point prefix to /path/to/simulator (don't include basefiles in the path)
./tests/bare_metal/tests_serial.sh
./tests/bare_metal/tests_parallel.sh
```

You should see two SUCCESS messages

</details>

<a name="run_tests_works_docker"></a> 
## Docker works
<details>

1. create and run a container from your "simulator_compile" image
2. change directories (should already be in the correct directory)
3. edit basefiles/batsim_environment.sh 
4. run test_serial script
5. view result
6. exit docker

```
docker run -it --name sim_test simulator_compile:latest
inside docker> cd /home/sim/simulator/basefiles
inside docker> # edit ./batsim_environment.sh  # prefix should be /home/sim/simulator
inside docker> ./tests/docker/tests_serial.sh
inside docker> exit

```
You should see a SUCCESS message

</details>

<a name="run_tests_works_charliecloud"></a> 
## CharlieCloud works

<details>

1. change directories
2. edit basefiles/batsim_environment.sh
3. run test_serial script
4. view result
5. run test_parallel script
6. view result
```
cd /path/to/simulator/basefiles
# edit ./batsim_environment.sh   
# make sure you point prefix to /path/to/simulator (don't include basefiles in the path)
./tests/charliecloud/tests_serial.sh
./tests/charliecloud/tests_parallel.sh
```
You should see two SUCCESS messages

</details>


<!-- ----------------------------------------------------------------  Verifying Paper --------------------------------------------- -->
***


<a name="run_tests_verify"></a>
# Verifying Paper

While we invite you to get the same results we did by running our simulations, there are some things to consider

- We used a 12 node cluster with 30 cores per node and 377GB RAM per node
    - In order to not run out of memory we used 26 tasks per node to limit memory usage.  Feel free to limit it even more.
- The simulations took at least 4 days total on our cluster
    - Of course it all depends on your cluster
- It is a bit ridiculous to think of doing it serially
- While it has been our intention to add seeds to our config files for random computations to become deterministic, at the time of this writing it is not deterministic.
    - With enough runs they would converge
    - You should get similar results as us with the 47 runs achieved from our config files, though not exact

<!-- ---------------------  Crash Course ------------------------------ -->


<a name="crash_course"></a>
## Crash Course To myBatchTasks.sh

<details>

You run our simulations using a script called myBatchTasks.sh <br />
For help:
```
cd simualtor/basefiles
./myBatchTasks.sh --help
```
### File and Output Folder

- The most important info to give it is the config file and the output folder
- If you provide just the name of the config file or just the name of the output folder, it will assume you are using the default
'configs' folder and the default 'experiments' folder respectively.
- You may not have space on these locations (particularly the output folder) so you can pass absolute paths to these locations.
    - 15GB is necessary for verifying our paper
- With the output folder **Make Sure**:
    - if using default locations (no slashes), that that folder does not exist in simulator/experiments/
    - if using absolute locations, that the leaf of the output folder does not exist

### Tasks Per Node

- Again, we used this property to limit how many simulations would run on a node and thus limit its memory usage
    - You will also want to use it to limit simulations to less than or equal to the amount of cores on your nodes

### Method

- Very important, this says how you deployed batsim.
    - Basically, for verifying the paper, you should only be using charliecloud or bare-metal
    - charliecloud is default

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


</details>

<!-- ---------------------  Squeue Monitoring ------------------------------ -->

<a name="squeue"></a>
## Squeue Monitoring

<details>

We use a certain format passed to squeue to see which simulations are still running.<br />
It is advised you do the same.  Add the following to your .bashrc :<br />
```
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

</details>

<!-- ---------------------  Verify Methods ------------------------------ -->

<a name="run_tests_verify_methods"></a>
## Verification Methods

<a name="run_tests_verify_bare_metal"></a>
### Bare-Metal Verification

<a name="run_tests_verify_bare_metal_parallel"></a>
#### Parallel

<details>

1. change directories
2. edit batsim_environment.sh if you have not already
3. determine number of tasks to run on each node
4. run myBatchTasks.sh filling in for `##`
5. monitor simulations using [squeue monitoring](#squeue)
6. [run analysis](#analysis)

```
cd /path/to/simulator/basefiles
#edit batsim_environment.sh if needed
./myBatchTasks.sh -f `pwd`/tests/configs/paper.config -o paper -m bare-metal -p tasks -t ##
```

</details>

<a name="run_tests_verify_bare_metal_serial"></a>
#### Serial

<details>

1. change directories
2. edit batsim_environment.sh if you have not already
3. run myBatchTasks.sh
4. wait for a very long time (years)
5. [run analysis](#analysis)

```
cd /path/to/simulator/basefiles
#edit batsim_environment.sh if needed
./myBatchTasks.sh -f `pwd`/tests/configs/paper.config -o paper -m bare-metal -p none
```

</details>

<a name="run_tests_verify_docker"></a>
### Docker Verification

<a name="run_tests_verify_docker_parallel"></a>
#### Parallel

<details>

**Not an option at this time**

</details>

<a name="run_tests_verify_docker_serial"></a>
#### Serial

<details>

1. start up docker container
    1. if already created use 'docker start'
    2. if not already created (from the tests) use 'docker run'
2. change directories (shouldn't need to)
3. edit batsim_environment.sh if you have not already
4. run myBatchTasks.sh
5. wait for a very long time (years)
6. [run analysis](#analysis)

##### i.
```
docker start -i sim_test
```

##### ii.
```
docker run -it --name sim_test simulator_compile:latest
```

```
inside docker>  cd /home/sim/simulator/basefiles
inside docker>  #edit batsim_environment.sh if you haven't
inside docker>  ./myBatchTasks.sh -f `pwd`/tests/configs/paper.config -o paper -m docker -p none
```

</details>


<a name="run_tests_verify_charliecloud"></a>
### CharlieCloud Verification

<a name="run_tests_verify_charliecloud_parallel"></a>
#### Parallel

<details>

1. change directories
2. edit batsim_environment.sh if you have not already
3. determine number of tasks to run on each node
4. run myBatchTasks.sh filling in for `##`
5. monitor simulations using [squeue monitoring](#squeue)
6. [run analysis](#analysis)

```
cd /path/to/simulator/basefiles
#edit batsim_environment.sh if needed
./myBatchTasks.sh -f `pwd`/tests/configs/paper.config -o paper -m charliecloud -p tasks -t ##
```

</details>

<a name="run_tests_verify_charliecloud_serial"></a>
#### Serial

<details>

1. change directories
2. edit batsim_environment.sh if you have not already
3. run myBatchTasks.sh
4. wait for a very long time (years)
5. [run analysis](#analysis)

```
cd /path/to/simulator/basefiles
#edit batsim_environment.sh if needed
./myBatchTasks.sh -f `pwd`/tests/configs/paper.config -o paper -m charliecloud -p none
```

</details>


<!-- ---------------------  Analysis ------------------------------ -->

<a name="analysis"></a>
## Analysis

<details>

### CharlieCloud and Bare-Metal

1. change directories
2. run analysis script
3. browse folders
    1. total_waiting_time
        1. comparisons 
            1. WD = 1 month; 2,4,8 days
            2. Binned
            3. Overall
        2. graphs
4. use image viewer to view pngs

```
cd /path/to/simulator/basefiles
source ../python_env/bin/activate
# you may have chosen a different location for the sim's data to go when invoking 'myBatchTasks.sh'.
# If this is the case use that path for --folder.
# run python3 ./tests/analysis.py --help for options
python3 ./tests/analysis.py --folder /path/to/simulator/experiments/paper --comparisons
```

Now `/path/to/simulator/basefiles/tests/paper_analysis` will house your various graphs

#### Browsing Folders

```
.../paper_analysis/total_waiting_time/graphs:
    if --all,--outliers, --non-outliers is selected you will have graphs here
    When --all or --non-outliers is selected you will have graphs with cut_ in front of the graph name
        These cut out any values past 2 standard deviations of the mean
    When --all or --outliers is selected you will have graphs without cut_ in front of the graph name
        These are graphs as-is.  They may not show much in terms of resolution since they include more extreme data


.../paper_analysis/total_waiting_time/comparisons:
    Comparisons are made regardless of the option given

    .../comparisons/comparisons_overall/
        Overall mean of the waiting times as the WD Units go from 1 to 8 subdivisions

    .../comparisons/<WD Unit>/
        Binned means of the waiting times in a certain WD Unit

```



</details>



<!-- ------------------------------------------------------------   Further Reading ----------------------------------------------- -->
***


<a name="further_reading"></a>
# Further Reading

<a name="config_files"></a>
## Config Files

If you would like to run other experiments, feel free to learn about our simulator and how to write a config file.
```
cd /path/to/simulator/basefiles
source ../python_env/bin/activate
python3 generate_config.py --help
```

You should see that you can pass it `--config-info <type>`

Once you are satisfied with your config file

Try running it using the 'myBatchTasks.sh' script












