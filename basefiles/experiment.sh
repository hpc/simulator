#!/bin/bash

date
echo "in experiment.sh"
hostname
#MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
#MY_PATH="$(cd -- "$MY_PATH" && pwd)"
MY_PATH=$basefiles
source $basefiles/batsim_environment.sh
echo "after source"
parallelMode="$1"
method="$2"

case $parallelMode in
    "tasks")
        jobPathA=( ${jobPathString})
        socketCountA=( ${socketCountString})
        experimentA=( ${experimentString})
        jobA=( ${jobString})
        idA=( ${idString})
        runA=( ${runString})
        srunCount=${#jobPathA[@]}
        echo "srunCount= $srunCount"
        case $method in
            "bare-metal" | "charliecloud")   
                for i in `seq 0 1 $(( $srunCount - 1 ))`;do
                    echo "real_start.py" && date
                    outputPath=`echo "${jobPathA[$i]}" | sed "s@:PATH:@@g"`
                    srun --ntasks=1 -c 1 --output ${outputPath}/output/slurm-%j.out --job-name="${folder}_${experimentA[$i]}_${jobA[$i]}j_${idA[$i]}i_${runA[$i]}r" \
                    $python_prefix/bin/python3 $basefiles/real_start.py --path ${jobPathA[$i]} --method $method --socketCount ${socketCountA[$i]} --sim-time $mySimTime &
                   
                done
                wait
                ;;
            *)
                echo "Error: parallelMode='tasks' but all that is allowed for method is 'bare-metal' or 'charliecloud' and you are using method=$method"
                exit 1
                ;;
        esac
        ;;
    "sbatch")
        case $method in
            "bare-metal" | "charliecloud")
                USER=$USER python3 $basefiles/real_start.py --path $jobPath --method $method --socketCount $socketCount --sim-time $mySimTime
                ;;
            *)
                echo "Error: parallelMode='sbatch' but all that is allowed for 'method' is 'bare-metal' or 'charliecloud' and you are using method=$method"
                exit 1
                ;;    
        esac
        ;;
    "background")
        case $method in
            "bare-metal" | "docker" | "charliecloud")
                echo ""
                echo ""
                echo "*****************************************"
                echo "basefiles=$basefiles"
                jobPath=$3
                socketCount=$4
                mySimTime=$5
                echo "python3 $basefiles/real_start.py --path $jobPath --method $method --socketCount $socketCount --sim-time $mySimTime"
                python3 $basefiles/real_start.py --path $jobPath --method $method --socketCount $socketCount --sim-time $mySimTime
                ;;

        esac
esac
echo "real_start.py" && date

#rm $jobPath/output/expe-out/out*
#rm $jobPath/output/expe-out/post_out_jobs.csv
#rm $jobPath/output/expe-out/raw_post_out_jobs.csv
#rm -rf $jobPath/output/expe-out/log/
date