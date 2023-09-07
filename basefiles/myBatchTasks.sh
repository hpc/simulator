#!/bin/bash
MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
export prefix="$(cd -- "$MY_PATH"/../ && pwd)"

source $prefix/basefiles/batsim_environment.sh
export basefiles=$prefix/basefiles
source $prefix/python_env/bin/activate

VALID_ARGS=$(getopt -o f:o:s:t:c:m:p:w:ha: --long file:,folder:,socket-start:,tasks-per-node:,cores-per-node:,method:,parallel-method:,wallclock-limit:,add-to-sbatch:,permissions:,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi
FILE1=false
FOLDER1=false
SOCKET_START=10000
TASKS_PER_NODE=false
CORES_PER_NODE=false
WALLCLOCK=' '
METHOD='charliecloud'
P_METHOD='tasks'
FOLDER1_ABS=false
FILE1_ABS=false
PERMISSIONS=false

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
            FILE1_DIR=$(dirname "$2")
            FILE1_BASE=$(basename "$2")
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
            FOLDER1_ABS=true
            FOLDER1="$2"
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
    --permissions)
        echo "perm: $2"
        PERMISSIONS="$2"
        shift 2
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
    myBatchTasks.sh -f <STR> -o <STR> (-p sbatch [-c <INT>] | -p tasks -t <INT> )[-m <STR>] [-s <INT>] [-w <STR>][--permissions <STR>]

Required Options:

    -f, --file <STR>                The config file.  Just the file name, the folder of where that file is
                                    is worked out from $PREFIX being set and default locations within

    -o, --folder  <STR>             Where to output all the results of the simulations.  Just the folder name of where
                                    to put stuff within the default locations ( $PREFIX/experiments/<folder_name>)

    -t, --tasks-per-node <INT>      How many tasks to put on each node
                                    Only used with --parallel-method 'tasks' and 'background'
                                    and mandatory with these parallel-methods

Optional Options:
    -a, --add-to-sbatch <STR>       Commands to add to sbatch, in the form:
                                    long:
                                        -a "--option_s value --option_t value --option_u --option"
                                    short/mixed:
                                        --add-to-sbatch "-s value -t value -u --option"

    -c, --cores-per-node <INT>      How many cores to use for each sbatch
                                    Only used with --parallel-method 'sbatch'
                                    Not mandatory

    -m, --method <STR>              What method to run batsim:
                                    'bare-metal' | 'docker' | 'charliecloud'
                                    [default: 'charliecloud']

    -p, --parallel-method <STR>     What method to spawn multiple batsims:
                                    'sbatch' | 'tasks' | 'none' | 'background'
                                    sbatch: individual sbatch commands for each sim
                                    tasks: --tasks-per-node sims per sbatch command, with enough sbatch's to complete config file generated sims
                                    none: no parallelism,only serial. Will run one sim after another (may take a VERY long time)
                                    background: will try to achieve parallelism by backgrounding each sim, backgrounding (--tasks-per-node - 1) sims before waiting
                                    [default: 'tasks']

    -s, --socket-start <INT>        What socket number to start at. You must do your own housekeeping of sockets.  If you already
                                    have 100 sims going and you started at 10,000, then you will want to do your next set of sims at 10,100 for example
                                    You can use higher numbers.  I've used numbers up to 300,000
                                    [default: 10000]

    -w, --wallclock-limit <STR>     How long your jobs will take as reported to SLURM
                                    Will leave it up to slurm if not chosen.  Sometimes SLURM will set it for UNLIMITED
                                    STR is in format:
                                    "minutes", "minutes:seconds", "hours:minutes:seconds", 
                                    "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
                                    ex: '48' , '48:30', '2:48:30'  ==   48 minutes, 48.5 minutes, 2hours 48.5 minutes
                                        '3-0' , '3-12:0', '3-12:30:0' ==  3days, 3days 12 hours, 3 days 12.5 hours
                                        
    --permissions <STR>             permissions to give files/folders after generate_config.py is run but before run-experiments.py is run.
                                    It is still suggested to use SLURM_UMASK in batsim_environment.sh for files made during the simulations.
                                    STR = The octal numbers for the permissions
                                    ex: '--permissions 777' = rwxrwxrwx
                                        '--permissions 750' = rwxr-x---
                                        '--permissions 755' = rwxr-xr-x
    -h, --help                      Display this usage page

EOF
exit 1
fi
mkdir -p $basefiles/workloads
date


if [ $P_METHOD = 'tasks' ];then
    case $METHOD in
        'charliecloud')
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --write -- /bin/bash -c "mkdir -p /mnt/prefix;mkdir -p /mnt/FOLDER1;mkdir -p /mnt/FILE1"
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config"
            ;;
        'bare-metal')
            python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config
            ;;
        'docker')
            echo "parallel-method 'tasks' is not valid with method 'docker'"
    esac
    if [ $PERMISSIONS != false ];then
        chmod -R $PERMISSIONS $FOLDER1
    fi
    python3 $basefiles/run-experiments.py -i $FOLDER1  --method $METHOD --parallel-mode $P_METHOD --socket-start ${SOCKET_START} --tasks-per-node $TASKS_PER_NODE $WALLCLOCK --add-to-sbatch "$ADDED"
elif [ $P_METHOD = 'sbatch' ];then
    if [ $CORES_PER_NODE ];then
        CORES_PER_NODE="--cores-per-node $CORES_PER_NODE"
    else
        CORES_PER_NODE=""
    fi
    case $METHOD in
        'charliecloud')
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --write -- /bin/bash -c "mkdir -p /mnt/prefix;mkdir -p /mnt/FOLDER1;mkdir -p /mnt/FILE1"
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config"
            ;;
        'bare-metal')
            python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config
            ;;
        'docker')
            echo " parallel-method 'sbatch' is not valid with method 'docker' "
    esac
    if [ $PERMISSIONS != false ];then
        chmod -R $PERMISSIONS $FOLDER1
    fi
    python3 $basefiles/run-experiments.py -i $FOLDER1  --method $METHOD --parallel-mode $P_METHOD --socket-start ${SOCKET_START} --cores-per-node $CORES_PER_NODE $WALLCLOCK --add-to-sbatch "$ADDED"
elif [ $P_METHOD = 'none' ] || [ $P_METHOD = 'background' ]; then
    if [ $P_METHOD = 'none' ];then
        TASKS_PER_NODE=1
        P_METHOD='background'
    fi    

    case $METHOD in
        'charliecloud')
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --write -- /bin/bash -c "mkdir -p /mnt/prefix;mkdir -p /mnt/FOLDER1;mkdir -p /mnt/FILE1"
            $prefix/charliecloud/charliecloud/bin/ch-run $prefix/batsim_ch --bind ${prefix}:/mnt/prefix --bind ${FOLDER1_DIR}:/mnt/FOLDER1 --bind ${FILE1_DIR}:/mnt/FILE1 --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/prefix/basefiles;source /home/sim/simulator/python_env/bin/activate; python3 generate_config.py -i /mnt/FILE1/$FILE1_BASE -o /mnt/FOLDER1/$FOLDER1_BASE --output-config"
            ;;
        'bare-metal')
            python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config
            ;;
        'docker')
            prefix=/home/sim/simulator
            python3 $basefiles/generate_config.py -i $FILE1 -o $FOLDER1 --basefiles ${basefiles}  --output-config
            ;;
    esac
    if [ $PERMISSIONS != false ];then
        chmod -R $PERMISSIONS $FOLDER1
    fi
    python3 $basefiles/run-experiments.py -i $FOLDER1  --method $METHOD --parallel-mode $P_METHOD --socket-start ${SOCKET_START} --tasks-per-node ${TASKS_PER_NODE}
fi

