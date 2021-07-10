Using a cluster for Monte Carlo simulation

  We made use of a cluster at the NMC (New Mexico Consortium) to run all of our large-scale Monte Carlo Simulations.
  It consisted of 13 nodes with 30 cores on each node, so 30 jobs were able to run at one time on each node
  (390 jobs at one time)



Folders:
---------
configs                         -- Where the configuration files that you need to run the Monte
                                Carlo experiments are kept
                                
platforms                       -- Holds the 1490 nodes platform file.  All platforms that are
                                created after are based on this original, and are also put in
                                this folder
                                
workloads                       -- Holds all the created workloads




Files:
--------

aggregate_makespan.py           -- script to gather all the makespans from individual
                                experiments and Runs and average them into one file: 
                                total_makespan.csv
                                This is run after all simulations are finished.

aggregate_pass_fail.py          -- script to gather together all pass-fail runs and get a percent 
                                pass and percent fail.
                                This is run after all simulations are finished.
                               
change_platform.py              -- script to change a platform file's number of nodes
                                This is run automatically in the generate_config.py script.

change_workload.py              -- script that was originally made to change the number of nodes
                                a workload was associated with.  Some extra functionality was added.
                                This script is to save time, given that it is easier to just change
                                the number of nodes at the top of the file than generate a whole new 
                                workload if the only difference is the number of nodes.
                                This is run automatically in the generate_config.py script.
                                
deploy.sh                       -- Our script for deploying batsim, batsched, and robin on our
                                cluster.  This would need to be edited.

docopt.py                       -- A module used to develop very easy command line parsing.  A
                                "Usage" string is used to both be shown and parsed in order to setup 
                                the command line rules.
                                The c++ version was used in Batsim by Batsim's authors, as well.
                                Copyright (c) 2012 Vladimir Keleshev, <vladimir@keleshev.com>
                                https://github.com/docopt/docopt
                                Used in almost all of the python scripts.
                               
experiment.sh                   -- The shell script sent to SLURM through the "sbatch" command.  It
                                runs the python script "real_start.py", which runs the simulation 
                                and post processing.  It then deletes files that are not needed at 
                                the present time, out of necessity, due to limited storage.
                                This is run automatically by SLURM from sending it through the
                                "sbatch" command that is dispatched from the run_experiments.py 
                                script.
                               
generate_config_strings.py      -- A module that holds strings used to show the user of 
                                generate_config.py the correct way to write a config file and all 
                                the options therein.
                                Used in generate_config.py, specifically with the --config-info
                                option
                               
generate_config.py              -- The main script to setup the folders that are required for all
                                the simulations that will result from a config file.  It also 
                                generates the correct workloads and platforms and puts a tailored 
                                config file for each simulation in the appropriate places.  These 
                                tailored config files are read by real_start.py.
                                This script is intended to be the first script to be run by the
                                user, followed by run_experiments.py. However, myBatch combines the  
                                two.

generate_grizzly_workload.py    -- script that generates a workload based on portions of our
                                grizzly-cluster workload data.  This was not used in our paper.
                                Would be used by generate_config.py to generate workloads.

generate_synthetic_workload.py  -- script that generates a workload based on many options, most
                                using some kind of randomness.  
                                This is run automatically by generate_config.py based on the 
                                workload options set in the config file passed to it.

myBatch                         -- shell script that is passed to SLURM through "sbatch" that
                                combines generate_config.py and run_experiments.py
                                

pass-fail-processing.py         -- script that reads in the log file of the simulation and
                                determines if it passed or failed the pass-fail test and then writes 
                                the result to a file.
                                This is run automatically after a simulation if the pass-fail
                                setting was on in the config file.

post-processing.py              -- script that does all the needed processing of our additions 
                                to Batsim and outputs this as one big csv file called 
                                post_out_jobs.csv , for each simulation.  It also outputs            
                                makespan.csv and AAE.csv.
                                This is run automatically after a simulation.
                                
real_start.py                   -- Originally there was a start.py each job would run that pointed 
                                to this real_start.py, but we took out the need for start.py and we 
                                are left with only real_start.py.  This is the script that starts
                                our simulation.  It generates a .yaml file using a Batsim program 
                                called "robin" which is passed input based on a config file we pass 
                                to this "real_start.py" script.
                                Batsim uses sockets to talk to it's scheduler.  Having so many
                                sockets going at a time(one for each simulation) can have problems.
                                real_start.py takes a "socketCount" argument as the number of that
                                simulation's socket.  "run_experiments.py" will take a socket
                                number to start at and continually increment until all
                                simulations have been queued.  This start number is set in
                                myBatch.
                                This script is run automatically.  run_experiments.py calls
                                "sbatch" with experiment.sh. experiment.sh calls this script with
                                the correct parameters.
                                
run-experiments.py              -- script that takes as input a folder that holds all of the 
                                folders and files created with generate_config.py, and then queues, 
                                to SLURM using "sbatch",jobs based on what was in those folders.     
                                This script is intended to be the second script to be run by the     
                                user after running generate_config.py. However, myBatch combines the
                                two.
                                
start.sh                        -- shell script that sets up the correct environment for running
                                python scripts, "go" code, as well as batsim and batsched.
                                Used by myBatch.

start2.sh                       -- shell script that sets up the correct environment for running
                                python scripts, "go" code, as well as batsim and batsched.  
                                Basically the same as start.sh except it lacks the loading of cmake
                                and gcc.
                                Used by experiment.sh
                                
wl1.csv                         -- 500k resources,duration file that is used to make what one could
                                call a small-sized jobs workload.
                               
wl2.csv                         -- 500k resources,duration file that is used to make what one could
                                call a regular-grizzly-cluster-sized jobs workload.

wl3.csv                         -- 500k resources,duration file that is used to make what one could
                                call a medium-sized jobs workload.
                                                                
wl4.csv                         -- 500k resources,duration file that is used to make what one could
                                call a medium-high-sized jobs workload.
                                
wl5.csv                         -- 500k resources,duration file that is used to make what one could
                                call a large-sized jobs workload.
                                
wl6.csv                         -- 500k resources,duration file that is used to make what one could
                                call a full-sized jobs workload.                                 
                                
