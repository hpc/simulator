#!/usr/bin/bash
function requeue_this
{
    #run python script that handles everything
    echo "$SLURM_EXPORT_ENV"
    SLURM_EXPORT_ENV=`echo "$SLURM_EXPORT_ENV" | sed 's@'\''@\\'\''@g'`
    srun --ntasks=1 -c 1 ${python_prefix}/bin/python3 ${basefiles}/functions.py requeue "$SLURM_JOB_PARTITION" "$srunCount" "$SLURM_EXPORT_ENV" "$myTime" "$output" "$comment" "$addToSbatch" "$basefiles" "$parallelMode" "$method" "$signal_num" "$SLURM_JOB_ID" "$projectFolder" "$jobPathString" "$socketCountString" "$experimentString" "$jobString" "$idString" "$runString" "${ourPIDs[*]}" "$(( number + 1 ))" &
    wait
}

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
ourPIDs=()
case $parallelMode in
    "tasks")
        jobPathA=( ${jobPathString})
        socketCountA=( ${socketCountString})
        experimentA=( ${experimentString})
        jobA=( ${jobString})
        idA=( ${idString})
        runA=( ${runString})
        srunCount=${#jobPathA[@]}
        if [[ $number == "" ]];then
            number=0
        fi
        echo "srunCount= $srunCount"
        case $method in
            "bare-metal" | "charliecloud")   
                for i in `seq 0 1 $(( $srunCount - 1 ))`;do
                    echo "real_start.py" && date
                    outputPath=`echo "${jobPathA[$i]}" | sed "s@:PATH:@@g"`
                    srun --ntasks=1 -c 1 --output ${outputPath}/output/slurm-%j.out --job-name="${folder}_${experimentA[$i]}_${jobA[$i]}j_${idA[$i]}i_${runA[$i]}r" \
                    $python_prefix/bin/python3 $basefiles/real_start.py --path ${jobPathA[$i]} --method $method --socketCount ${socketCountA[$i]} --sim-time $mySimTime --requeue-num $number &
                    ourPIDs+=($!)
                   
                done
                if [[ $signal_num != "" ]];then
                  trap "requeue_this" $signal_num
                fi
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
                USER=$USER python3 $basefiles/real_start.py --path $jobPath --method $method --socketCount $socketCount --sim-time $mySimTime --requeue-num $number
                ourPIDs=($!)
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