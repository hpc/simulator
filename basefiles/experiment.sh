#!/bin/bash
echo "in experiment.sh"
hostname
source /home/cwalker/start2.sh
echo "after source"
#lsof -Pi :$socketCount -sTCP:LISTEN
#while [[ $? == 0 ]]
#do
#    socketCount=$(( $socketCount + 10000 ))
#    #if [[ $socketCount > 65534 ]]
#    #then
#    #    socketCount=33000
#    #fi
#    lsof -Pi :$socketCount -sTCP:LISTEN
#done
echo "real_start.py" && date
python3 /home/cwalker/basefiles/real_start.py --path $jobPath --socketCount $socketCount --sim-time $mySimTime
rm $jobPath/output/expe-out/out*
rm $jobPath/output/expe-out/post_out_jobs.csv
rm $jobPath/output/expe-out/raw_post_out_jobs.csv
#rm -rf $jobPath/output/expe-out/log/

