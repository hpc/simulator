#!/bin/bash
date
echo "in experiment.sh"
hostname
#setup some environment variables
source ./start2.sh
#run the simulation
python3 ./real_start.py --path $jobPath --socketCount $socketCount --sim-time $mySimTime

#remove log files and other files we don't need for average makespan
#get rid of these statements if you need more than average makespan and also if you have plenty of hard drive space
#plenty is on the order of 100's of TB when running many Runs for each experiment.
rm $jobPath/output/expe-out/out*
rm $jobPath/output/expe-out/post_out_jobs.csv
rm $jobPath/output/expe-out/raw_post_out_jobs.csv
rm -rf $jobPath/output/expe-out/log/
date
