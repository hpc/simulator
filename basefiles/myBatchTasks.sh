#!/usr/bin/bash
START_FROM_FIRST_CHECKPOINTED_FRAME_NB=-5
MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
export prefix="$(cd -- "$MY_PATH"/../ && pwd)"

. $prefix/basefiles/batsim_environment.sh
export basefiles=$prefix/basefiles
. $prefix/python_env/bin/activate

VALID_ARGS=$(getopt -o f:o:s:t:c:m:p:w:ha:S:P:F:K:DCId:L --long start-from-first-checkpointed-frame,discard-old-logs:,test-suite,skip-completed-sims,file:,folder:,socket-start:,tasks-per-node:,cores-per-node:,method:,parallel-method:,wallclock-limit:,add-to-sbatch:,permissions:,start-from-checkpoint:,start-from-checkpoint-keep:,start-from-frame:,discard-last-frame,ignore-does-not-exist,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi
FILE1=false
FOLDER1=false
SOCKET_START=10000
TASKS_PER_NODE=false
CORES_PER_NODE=false
WALLCLOCK=' '
METHOD='bare-metal'
P_METHOD='tasks'
FOLDER1_ABS=false
FILE1_ABS=false
PERMISSIONS=false
TEST_SUITE=""
START_FROM_CHECKPOINT=false
SKIP_COMPLETED=""
FRAME=0
KEEP=-1
DISCARD=""
DISCARD_LOGS=""
IGNORE_DOES_NOT_EXIST=""

eval set -- "$VALID_ARGS"
while true; do
  case "$1" in
    -f | --file)
        echo "f $2"
        myString="$2"
        grep "/" <<<"$myString" > /dev/null
        if [ $? -eq 0 ];then
            FILE1_ABS=true
            FILE1="$2"
            #is ./ being entered?
            if [[ $myString == "./" ]];then
                tmp="$(cd -- "./" && pwd)"
                GLOBIGNORE="strippedComments.config"
                FILE1="$tmp/$(ls *.config)"
                unset GLOBIGNORE
            fi
            FILE1_DIR=$(dirname "$FILE1")
            FILE1_BASE=$(basename "$FILE1")
        else
            FILE1_DIR="$prefix/configs"
            FILE1_BASE="$2"
            FILE1="$FILE1_DIR/$FILE1_BASE"
        fi
        shift 2
        ;;
    -o | --folder)
        echo "o $2"
        myString="$2"
        grep "/" <<<"$myString" > /dev/null
        if [ $? -eq 0 ];then
            mkdir -p "$myString"
            FOLDER1_ABS=true
            FOLDER1="$(cd -- "$2" && pwd)"
            FOLDER1_DIR=$(dirname "$2")
            FOLDER1_BASE=$(basename "$2")
        else
            FOLDER1_DIR="$prefix/experiments"
            FOLDER1_BASE="$2"
            FOLDER1="$FOLDER1_DIR/$FOLDER1_BASE"
        fi
        shift 2
        ;;
    -s | --socket-start)
        echo "s $2"
        SOCKET_START="$2"
        shift 2
        ;;
    -t | --tasks-per-node)
        echo "t $2"
        TASKS_PER_NODE="$2"
        shift 2
        ;;
    -c | --cores-per-node)
        echo "c $2"
        CORES_PER_NODE="$2"
        shift 2
        ;;
    -a | --add-to-sbatch)
        echo "a $2"
        ADDED="$2"
        shift 2
        ;;
    -m | --method)
        echo "m $2"
        METHOD="$2"
        shift 2
        ;;
    -p | --parallel-method)
        echo "p $2"
        P_METHOD="$2"
        shift 2
        ;;
    -w | --wallclock-limit)
        echo "w $2"
        WALLCLOCK="--time $2"
        shift 2
        ;;
    -P | --permissions)
        echo "perm: $2"
        PERMISSIONS="$2"
        shift 2
        ;;
    --test-suite)
        TEST_SUITE=" --test-suite"
        shift 1
        ;;
    -S | --start-from-checkpoint)
        START_FROM_CHECKPOINT=$2
        shift 2
        ;;
    -C | --skip-completed-sims)
        SKIP_COMPLETED=" --skip-completed-sims "
        shift 1
        ;;
    -D | --discard-last-frame)
        DISCARD=" --discard-last-frame "
        shift 1
        ;;
    -d | --discard-old-logs)
        DISCARD_LOGS=" --discard-old-logs $2 "
        shift 2
        ;;
    -F | --start-from-frame)
        FRAME=$2
        shift 2
        ;;
    -L | --start-from-first-checkpointed-frame)
        FRAME=$START_FROM_FIRST_CHECKPOINTED_FRAME_NB
        START_FROM_CHECKPOINT=1
        shift 1
        ;;
    -K | --start-from-checkpoint-keep)
        KEEP=$2
        shift 2
        ;;
    -I | --ignore-does-not-exist)
        IGNORE_DOES_NOT_EXIST=" --ignore-does-not-exist"
        shift 1
        ;;
    -h | --help)
        break
        ;;
    --) shift; 
        break 
        ;;
  esac
done
methods=( 'bare-metal' 'docker' 'charliecloud')
echo ${methods[@]} | grep -w -q $METHOD
method_isin_methods=$?
if [ $FILE1 = false ] || [ $FOLDER1 = false ] ||  \
    ( [ $P_METHOD = 'tasks' ] && [ $TASKS_PER_NODE = false ] ) || \
    ( [ $P_METHOD = 'tasks' ] && [ $CORES_PER_NODE != false ]) || \
    ( [ $P_METHOD = 'sbatch' ] && [ $TASKS_PER_NODE != false ]) || \
    ( [ $P_METHOD = 'none' ] && ( [ $TASKS_PER_NODE != false ] || [ $CORES_PER_NODE != false ] ) ) || \
    [ $method_isin_methods -eq 1 ];then
    cat <<"EOF"


    myBatchTasks.sh         automates the generate-config script and run-experiments script.
                            Meant to be run from the command line and probably put into the background.
                            NOTE: make sure $prefix is set to the folder that houses basefiles, charliecloud, batsim_ch, python_env, experiments, and configs

Usage:
    myBatchTasks.sh  -f <STR> -o <STR> [options]
      deployment opts:         [-m 'bare-metal' | -m 'docker' | -m 'charliecloud' ]
      parallel opts:           (-p sbatch [-c <INT>] | -p tasks -t <INT> | -p background [-t <INT>] | -p none)
      opts:                    [-s <INT>] [-w <STR>][--permissions <STR>] [--add-to-sbatch <STR>] [--skip-completed-sims]
      checkpointing opts:      [--start-from-checkpoint <INT>] [--start-from-checkpoint-keep <INT>] [--discard-old-logs <INT>]  
      checkpoint frame opts:   [--discard-last-frame] [--start-from-frame <INT>] [--start-from-first-checkpointed-frame] 
      checkpointing opts:      [--ignore-does-not-exist]

Required Options:

    -f, --file <STR>                        The config file.  Just the file name, the folder of where that file is
                                            is worked out from $PREFIX being set and default locations within

    -o, --folder  <STR>                     Where to output all the results of the simulations.  Just the folder name of where
                                            to put stuff within the default locations ( $PREFIX/experiments/<folder_name>)

    -t, --tasks-per-node <INT>              How many tasks to put on each node
                                            Only used with --parallel-method 'tasks' and 'background'
                                            and mandatory with these parallel-methods

Optional Options:
    -a, --add-to-sbatch <STR>               Commands to add to sbatch, in the form:
                                            long:
                                                -a "--option_s value --option_t value --option_u --option"
                                            short/mixed:
                                                --add-to-sbatch "-s value -t value -u --option"

    -c, --cores-per-node <INT>              How many cores to use for each sbatch
                                            Only used with --parallel-method 'sbatch'
                                            Not mandatory

    -m, --method <STR>                      What method to run batsim:
                                            'bare-metal' | 'docker' | 'charliecloud'
                                            [default: 'bare-metal']

    -p, --parallel-method <STR>             What method to spawn multiple batsims:
                                            'sbatch' | 'tasks' | 'none' | 'background'
                                            sbatch: individual sbatch commands for each sim
                                            tasks: --tasks-per-node sims per sbatch command, with enough sbatch's to complete config file generated sims
                                            none: no parallelism,only serial. Will run one sim after another (may take a VERY long time)
                                            background: will try to achieve parallelism by backgrounding each sim, backgrounding (--tasks-per-node - 1) sims before waiting
                                            [default: 'tasks']

    -s, --socket-start <INT>                What socket number to start at. You must do your own housekeeping of sockets.  If you already
                                            have 100 sims going and you started at 10,000, then you will want to do your next set of sims at 10,100 for example
                                            You can use higher numbers.  I've used numbers up to 300,000
                                            [default: 10000]

    -w, --wallclock-limit <STR>             How long your jobs will take as reported to SLURM
                                            Will leave it up to slurm if not chosen.  Sometimes SLURM will set it for UNLIMITED
                                            STR is in format:
                                            "minutes", "minutes:seconds", "hours:minutes:seconds", 
                                            "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
                                            ex: '48' , '48:30', '2:48:30'  ==   48 minutes, 48.5 minutes, 2hours 48.5 minutes
                                                '3-0' , '3-12:0', '3-12:30:0' ==  3days, 3days 12 hours, 3 days 12.5 hours
                                        
    -P, --permissions <STR>                 permissions to give files/folders after generate_config.py is run but before run-experiments.py is run.
                                            It is still suggested to use SLURM_UMASK in batsim_environment.sh for files made during the simulations.
                                            STR = The octal numbers for the permissions
                                            ex: '--permissions 777' = rwxrwxrwx
                                                '--permissions 750' = rwxr-x---
                                                '--permissions 755' = rwxr-xr-x

    --test-suite                            set this flag to create current_progress.log in one folder up from FOLDER1

    -C, --skip-completed-sims               Set this to skip sims that are in progress.log as completed
                                            [default: false]
Checkpoint Batsim Options:

    -S, --start-from-checkpoint <INT>       Set this if starting from a checkpoint.  The <INT> is the number of the checkpoint.
                                            Typically '1', the latest
                                            [default: false]

    -D, --discard-last-frame                Used in conjunction with --start-from-checkpoint and can be used with --start-from-frame
                                            Does not make sense to use with --start-from-checkpoint-keep
                                            Flag to give the following behavior:
                                                Will not change any of the kept expe-out_#'s and will not keep the current expe-out

    -d, --discard-old-logs <INT>            discards all logs except the INT last ones
                                            default is -1, will not discard any
                                            [default: -1]

    -K, --start-from-checkpoint-keep <INT>  Used in conjunction with --start-from-checkpoint
                                            Will keep expe-out_1 through exp-out_<INT>.  Only use with --start-from-checkpoint
                                            When starting from checkpoint, the current expe-out folder becomes expe-out_1.
                                            Previous expe-out_1 will become expe-out_2 if keep is set to 2
                                            If you have expe-out_1,expe-out_2,expe-out_3 and keep is 3:
                                                will move expe-out_1 to expe-out_2
                                                will move expe-out_2 to expe-out_3
                                                will delete old expe-out_3
                                            default is -1 which is 1 except the config file trumps it
                                            [default: -1]

    -F, --start-from-frame <INT>            Only used with --start-from-checkpoint and in conjunction with --start-from-checkpoint-keep
                                            Will use the expe-out_<INT> folder to look for the checkpoint data
                                                So if you were invoking --start-from-checkpoint-keep 2, you would have
                                                expe-out_1 and expe-out_2,   once you started from a checkpoint twice.
                                                If you use --start-from-frame 2 you will be using the checkpoint_[--start-from-checkpoint]
                                                folder located in the expe-out_2 folder ( the expe-out_[--start-from-frame] folder)
                                            Here, '0' is the original expe-out folder that becomes expe-out_1
                                            If --discard-last-frame is used, then default here is 1. 0 is not allowed and will become 1 if used.
                                            [default: 0]
    -L, 
     --start-from-first-checkpointed-frame  Start from the latest checkpoint available.  Will go through all frames and choose the most recent 
                                            one that has a checkpoint_1 folder

    -I, --ignore-does-not-exist             Normally if the path to one of the checkpoints does not exist it will ERROR out and stop.
                                            This option tells it that some paths may not exist, but run the others that do,
                                            and not to alter anything in the paths that do not exist.

    -h, --help                              Display this usage page

EOF
exit 1
fi
mkdir -p $basefiles/workloads
date

#first check file
echo -e "\n\n *********************  Checking JSON config file  *********************\n"

python3 $MY_PATH/stripJsonComments.py --input $FILE1 --output STDOUT | python3 -m json.tool 1>/dev/null
if [ $? -eq 1 ];then
    echo -e "\n!!!!!!!!!!!!!!!!!!!!!  ERROR with Json File.  See message above  !!!!!!!!!!!!!!!!!!!!!\n"
    exit
else
    echo "*********************  JSON Check Appears To Be SUCCESSFUL *********************"
fi
python3 $basefiles/alphabetize_json.py -i $basefiles/configIniSchema.json
mkdir $FOLDER1 > /dev/null 2>&1
echo -e "{ \"generate_config\": true }" > $FOLDER1/config_state.log
if [ $P_METHOD = 'tasks' ];then
    case $METHOD in
        'charliecloud')
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --write -- /bin/bash -c "mkdir -p /mnt/prefix;mkdir -p /mnt/FOLDER1;mkdir -p /mnt/FILE1"
            if [ $START_FROM_CHECKPOINT != false ];then
                $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config --start-from-checkpoint $START_FROM_CHECKPOINT --start-from-frame $FRAME $IGNORE_DOES_NOT_EXIST --start-from-checkpoint-keep $KEEP $DISCARD $DISCARD_LOGS $TEST_SUITE $SKIP_COMPLETED" 
            else
                $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config $TEST_SUITE $SKIP_COMPLETED $DISCARD_LOGS"
            fi
            ;;
        'bare-metal')
            if [ $START_FROM_CHECKPOINT != false ];then
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config --start-from-checkpoint $START_FROM_CHECKPOINT --start-from-frame $FRAME $IGNORE_DOES_NOT_EXIST --start-from-checkpoint-keep $KEEP $DISCARD $DISCARD_LOGS $TEST_SUITE $SKIP_COMPLETED
            else
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config $TEST_SUITE $SKIP_COMPLETED $DISCARD_LOGS
            fi
            ;;
        'docker')
            echo "parallel-method 'tasks' is not valid with method 'docker'"
    esac
    if [ $PERMISSIONS != false ];then
        chmod -R $PERMISSIONS $FOLDER1
    fi
    if [[ $TEST_SUITE != ""  ]]; then
        progress_dir="$FOLDER1_DIR"
    else
        progress_dir="${FOLDER1_DIR}/${FOLDER1_BASE}"
    fi
    if ! [[ -f "$progress_dir/current_progress.log" ]]; then
        cat <<EOF > $progress_dir/current_progress.log
{
 "progress":true    
}
EOF
    fi

    python3 $basefiles/run-experiments.py -i $FOLDER1  --method $METHOD --parallel-mode $P_METHOD --socket-start ${SOCKET_START} --tasks-per-node $TASKS_PER_NODE $WALLCLOCK $SKIP_COMPLETED --add-to-sbatch "$ADDED"
elif [ $P_METHOD = 'sbatch' ];then
    if [ $CORES_PER_NODE ];then
        CORES_PER_NODE="--cores-per-node $CORES_PER_NODE"
    else
        CORES_PER_NODE=""
    fi
    case $METHOD in
        'charliecloud')
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --write -- /bin/bash -c "mkdir -p /mnt/prefix;mkdir -p /mnt/FOLDER1;mkdir -p /mnt/FILE1"
            if [ $START_FROM_CHECKPOINT != false ];then
                $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config --start-from-checkpoint $START_FROM_CHECKPOINT --start-from-frame $FRAME $IGNORE_DOES_NOT_EXIST --start-from-checkpoint-keep $KEEP $DISCARD $DISCARD_LOGS $TEST_SUITE $SKIP_COMPLETED"
            else
                $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config $TEST_SUITE $SKIP_COMPLETED $DISCARD_LOGS"
            fi
            ;;
        'bare-metal')
            if [ $START_FROM_CHECKPOINT != false ];then
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config --start-from-checkpoint $START_FROM_CHECKPOINT --start-from-frame $FRAME $IGNORE_DOES_NOT_EXIST --start-from-checkpoint-keep $KEEP $DISCARD $DISCARD_LOGS $TEST_SUITE $SKIP_COMPLETED
            else    
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config $TEST_SUITE $SKIP_COMPLETED $DISCARD_LOGS
            fi
            ;;
        'docker')
            echo " parallel-method 'sbatch' is not valid with method 'docker' "
    esac
    if [ $PERMISSIONS != false ];then
        chmod -R $PERMISSIONS $FOLDER1
    fi
    if [[ $TEST_SUITE != "" ]]; then
        progress_dir="$FOLDER1_DIR"
    else
        progress_dir="${FOLDER1_DIR}/${FOLDER1_BASE}"
    fi
    if ! [[ -f "$progress_dir/current_progress.log" ]]; then
        cat <<EOF > $progress_dir/current_progress.log
{
 "progress":true    
}
EOF
    fi
    python3 $basefiles/run-experiments.py -i $FOLDER1  --method $METHOD --parallel-mode $P_METHOD --socket-start ${SOCKET_START} --cores-per-node $CORES_PER_NODE $WALLCLOCK $SKIP_COMPLETED --add-to-sbatch "$ADDED"
elif [ $P_METHOD = 'none' ] || [ $P_METHOD = 'background' ]; then
    if [ $P_METHOD = 'none' ];then
        TASKS_PER_NODE=1
        P_METHOD='background'
    fi    

    case $METHOD in
        'charliecloud')
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --write -- /bin/bash -c "mkdir -p /mnt/prefix;mkdir -p /mnt/FOLDER1;mkdir -p /mnt/FILE1"
            if [ $START_FROM_CHECKPOINT != false ];then
                $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config --start-from-checkpoint $START_FROM_CHECKPOINT --start-from-frame $FRAME $IGNORE_DOES_NOT_EXIST --start-from-checkpoint-keep $KEEP $DISCARD $DISCARD_LOGS $TEST_SUITE $SKIP_COMPLETED"
            else
                $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config $TEST_SUITE $SKIP_COMPLETED $DISCARD_LOGS"
            fi
            ;;
        'bare-metal')
            if [ $START_FROM_CHECKPOINT != false ];then
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config --start-from-checkpoint $START_FROM_CHECKPOINT --start-from-frame $FRAME $IGNORE_DOES_NOT_EXIST --start-from-checkpoint-keep $KEEP $DISCARD $DISCARD_LOGS $TEST_SUITE $SKIP_COMPLETED
            else
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config $TEST_SUITE $SKIP_COMPLETED $DISCARD_LOGS
            fi
            ;;
        'docker')
            prefix=/home/sim/simulator
            if [ $START_FROM_CHECKPOINT != false ];then
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config --start-from-checkpoint $START_FROM_CHECKPOINT --start-from-frame $FRAME $IGNORE_DOES_NOT_EXIST --start-from-checkpoint-keep $KEEP $DISCARD $DISCARD_LOGS $TEST_SUITE $SKIP_COMPLETED
            else
                python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config $TEST_SUITE $SKIP_COMPLETED $DISCARD_LOGS
            fi
            ;;
    esac
    if [ $PERMISSIONS != false ];then
        chmod -R $PERMISSIONS $FOLDER1
    fi
    if [[ $TEST_SUITE != "" ]]; then
        progress_dir="$FOLDER1_DIR"
    else
        progress_dir="${FOLDER1_DIR}/${FOLDER1_BASE}"
    fi
    if ! [[ -f "$progress_dir/current_progress.log" ]]; then
        cat <<EOF > $progress_dir/current_progress.log
{
 "progress":true    
}
EOF
    fi
    python3 $basefiles/run-experiments.py -i $FOLDER1  --method $METHOD --parallel-mode $P_METHOD --socket-start ${SOCKET_START} --tasks-per-node ${TASKS_PER_NODE} $SKIP_COMPLETED
fi
