#!/bin/bash

function get_interval()
{
    read -ra ourInterval <<<"$1"
    local numbers=()
    for i in "${ourInterval[@]}";do
        grep "-"<<<$i > /dev/null
        if [ $? -eq 0 ];then
            #there is a dash
            IFS=- read start end <<< "$i"
            mySequence=`seq $start 1 $end`
            numbers=(${numbers[*]} ${mySequence[*]})
        else
            numbers=(${numbers[*]} $i)
        fi
    done
    echo "${numbers[*]}"
}
print_mem()
{
    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    if [[ $divideBy == -1 ]];then
            myOutput="$myOutput|\\033[${color}m`echo "$entry" \
            | awk -F, -v field=$field '{num=$field;if (num>2**30){div=2**30;u="TiB"}else if (num>2**20){div=2**20;u="GiB"}else if (num>2**10){div=2**10;u="MiB"}else{div=1;u="KiB"};num=int(num/div) ;printf("%'"'"'d %s",num,u)}'`\\033[0m"
    else
            myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, -v field=$field -v div=$divideBy -v u=$memSize '{num=($field/div);num=int(num);printf("%'"'"'d %s",num,u)}'`\\033[0m"
    fi
}
print_number()
{
    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    number=$(echo "$entry" |awk -F, -v field=$field '{printf("%'"'"'d",$field)}')
    myOutput="$myOutput|\\033[${color}m$number\\033[0m"
}
print_entry()
{
    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    number=$(echo "$entry" |awk -F, -v field=$field '{printf("%s",$field)}')
    myOutput="$myOutput|\\033[${color}m$number\\033[0m"
}


completed_jobs()
{
    color=$color1; field=1; name="actually_completed_jobs"; print_number;
    color=$color2; field=2; name="nb_jobs"; print_number;
}

percent_done()
{
    color=$color3; field=3; name="percent_done"; print_entry;
}
times()
{
    color=$color4; field=4; name="real_time"; print_entry;
    color=$color5; field=5; name="sim_time"; print_entry;
}
queue_size()
{
    color=$color6; field=6; name="queue_size"; print_number;
}
schedule_size()
{
    color=$color7; field=7; name="schedule_size"; print_number;
}
schedule_info()
{
    queue_size
    schedule_size
    color=$color8; field=8; name="nb_jobs_running"; print_number;
}
utilization()
{
    color=$color9; field=9; name="utilization"; print_number;
    color=$color10; field=10; name="utilization_no_resv"; print_number;
}
mem_avail()
{
        
    color=$color11; field=11; name="node_mem_total"; print_mem;
    color=$color12; field=12; name="node_mem_avail"; print_mem;
        
}
mem_batsim()
{
    color=$color13; field=13; name="batsim_USS"; print_mem;
    color=$color14; field=14; name="batsim_PSS"; print_mem;
    color=$color15; field=15; name="batsim_RSS"; print_mem;
}
mem_batsched()
{
    color=$color16; field=16; name="batsched_USS"; print_mem;
    color=$color17; field=17; name="batsched_PSS"; print_mem;
    color=$color18; field=18; name="batsched_RSS"; print_mem;
}




function print_output()
{
        color1=$light_blue
        color2=$gold
        color3=$dark_purple
        color4=$blue
        color5=$dark_red
        color6=$dark_green
        color7=$light_purple
        color8=$green
        color9=$dark_yellow
        color10=$dark_orange
        color11=$dark_grey
        color12=$light_grey
        color13=$dark_teal
        color14=$teal
        color15=$light_teal
        color16=$dark_pink
        color17=$pink
        color18=$light_pink
        space=" "
    if [ $all = true ] || [ $print = false ];then
        space=""
        completed_jobs
        percent_done
        times
        schedule_info
        utilization
        mem_avail
        mem_batsim
        mem_batsched
        echo -e "$myOutput"
    else

        
        if [ $completed = true ];then
            completed_jobs
        fi
        if [ $percent = true ];then
            percent_done
        fi
        if [ $timeO = true ];then
            times
        fi
        if [ $scheduleInfo = true ];then
            schedule_info
        elif [ $queue = true ];then
            queue_size
            if [ $schedule = true ];then
                schedule_size
            fi
        elif [ $schedule = true ];then
            schedule_size
        fi
        if [ $utilization = true ];then
            utilization
        fi
        if [ $memory != false ];then
            

            case "$memory" in
            "both")
                mem_batsim
                mem_batsched
                ;;
            "batsim")
                mem_batsim                
                ;;
            "batsched")
                mem_batsched
                ;;
            "all")
                mem_avail
                mem_batsim
                mem_batsched
                ;;
            "available")
                mem_avail
                ;;
            esac
        fi
        
        echo -e "$myOutput"
    fi
}


MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
export prefix="$(cd -- "$MY_PATH"/../ && pwd)"

source $prefix/basefiles/batsim_environment.sh
export basefiles=$prefix/basefiles
source $prefix/python_env/bin/activate

VALID_ARGS=$(getopt -o i:apcm:qsd:r:e:j:b:HM:tSu --long input:,all,percent,completed,time,memory:,memory-size:,schedule-info,utilization,queue-size,schedule-size,experiment:,job:,id:,run:,before:,head,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi
input=false
experiment=false
job=false
id=false
run=false
percent=false
completed=false
timeO=false
memory=false
queue=false
scheduleInfo=false
utilization=false
schedule=false
before=1
all=false
head=false
memSize="KiB"
divideBy=1
print=false


eval set -- "$VALID_ARGS"
while true; do
  case "$1" in
    -i | --input)
        echo "i $2"
        myString="$2"
        grep "/" <<<"$myString" > /dev/null
        if [ $? -eq 0 ];then
            input="$2"
            input_dir=$(dirname "$2")
            input_base=$(basename "$2")
        else
            input_dir="$prefix/experiments"
            input_base="$2"
            input="$input_dir/$input_base"
        fi
        shift 2
        ;;
     -e | --experiment)
        echo "e $2"
        experiment="$2"
        shift 2
        ;;
    -j | --job)
        echo "j $2"
        job="$2"
        shift 2
        ;;
    -d | --id)
        echo "id $2"
        id="$2"
        shift 2
        ;;
    -r | --run)
        echo "r $2"
        run="$2"
        shift 2
        ;;
    -a | --all)
        echo "a"
        all=true
        print=true
        shift 1
        ;;
    -p | --percent)
        echo "p"
        percent=true
        print=true
        shift 1
        ;;
    -c | --completed)
        echo "c"
        completed=true
        print=true
        shift 1
        ;;
    -t | --time)
        echo "t"
        timeO=true
        print=true
        shift 1
        ;;
    -m | --memory)
        echo "m $2"
        print=true
        memory="$2"
        shift 2
        ;;
    -M | --memory-size)
        echo "M $2"
        memSize="$2"
        case $memSize in
                "KB" | "K")
                    divideBy=1
                    memSize="KiB"
                    ;;
                "MB" | "M")
                    divideBy=1024
                    memSize="MiB"
                    ;;
                "GB" | "G")
                    divideBy=1048576
                    memSize="GiB"
                    ;;
                "TB" | "T")
                    divideBy=1073741824
                    memSize="TiB"
                    ;;
                "H")
                    divideBy=-1
                    ;;
        esac
        shift 2
        ;;
    -S | --schedule-info)
        echo "S"
        print=true
        scheduleInfo=true
        shift 1
        ;;
    -q | --queue-size)
        echo "q"
        print=true
        queue=true
        shift 1
        ;;
    -s | --schedule-size)
        echo "s"
        print=true
        schedule=true
        shift 1
        ;;
    -u | --utilization)
        echo "u"
        print=true
        utilization=true
        shift 1
        ;;
    -b | --before)
        echo "b $2"
        before=$2
        shift 2
        ;;
    -H | --head)
        echo "head"
        head=true
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
if [ $input = false ];then
cat <<"EOF"

progress.sh: used to show the progress of all simulations in a folder, or just certain ones, with options for what to show.

Usage:
    progress.sh -i <folder> [-e <folder>] [-j <array string>] [-d <array string>] [-r <array string>] 
                            [-b <int>] [-H] [-p] [-c] [-q] [-s] [-m <batsim|batsched|both|all|available>] [-M K|M|G|T|H] 

Required Options:
    -i, --input <folder>           Where the experiments are.  This is supposed to be the outer folder passed to ./myBatchTasks.sh
                                   If it has a forward slash '/' in the name it will assume it is an absolute path.
                                   If it does not have a forward slash '/' in the name it will assume it is located in "$prefix/experiments/<input>"
Optional Options:

Which-Simulation Options:

    -e, --experiment <folder>      If you want to focus on just one experiment (in the sense of config files where there was an input and output json for each experiment)
                                   then use this to enter the folder.  The path retrieved will then be ".../<input>/<experiment>/*"
    
    -j, --job <array string>       If you want to focus on just one job (in the sense of folders named experiment_#) then use this to enter the folder number.
                                   If used with --experiment then it will retrieve paths ".../<input>/<experiment>/experiment_<job>/*
                                   If not used with --experiment, then it will retrieve paths ".../<input>/*/experiment_<job>/*
                                   If multiple jobs are wanted then put the job numbers into a string, for example:
                                   '-j "1 2-5 10"'  will gather experiment_1,experiment_2,experiment_3,experiment_4,experiment_5, and experiment_10

    -d, --id <array string>        If you want to focus on just one id (in the sense of folders named id_#) then use this to enter the folder number.
                                   Basically the same as --job as far as how it works, except we focus on the id(s)

    -r, --run                      If you want to focus on just one run (in the sense of folders named Run_#) then use this to enter the folder number.
                                   Basically the same as --job and --id as far as how it works, except we focus on the run(s)

What-Info Options:

    -b, --before <int>             The amount of entries, starting from the last one, to include

    -H, --head                     Print the first entry in the out_extra_info.csv file first ( possilbe use is to check on how long the sim has been going )

    -a, --all                      Print out all data in the entry.  Default if nothing else is chosen to print.

    -p, --percent                  Include the percentage done that the sim has done

    -c, --completed                Include the amount of ACTUALLY completed jobs and TOTAL jobs

    -t, --time                     Include the real-time and sim-time
    
    -S, --schedule-info            Include queue-size,schedule-size,nb-jobs-running

    -q, --queue-size               Include the queue-size in output

    -s, --schedule-size            Include the schedule-size in output

    -u, --utilization              Include utilization and utilization-without-reservations

    -m, --memory <string>          Include the memory usage.  Will include the USS,PSS,RSS for "batsim|batsched|both".  Other options are "all|available"

    -M, --memory-size              When displaying memory, what size to display: KB | MB | GB | TB | H.  Single letter is fine too:  K | M | G | T | H
                                   This will actually be in KiB, MiB, GiB, or TiB
                                   H signifies you want human-readable units.  This is the largest unit that makes sense for the data.
                                   [default: KB]

    -h, --help                     Display this usage page

EOF
fi
black="48;5;16"
gold="48;5;94"
dark_grey="48;5;235"
grey="48;5;238"
light_grey="48;5;243"
dark_blue="48;5;17"
blue="48;5;21"
light_blue="48;5;33"
dark_green="48;5;22"
green="48;5;28"
light_green="48;5;34"
dark_purple="48;5;56"
purple="48;5;57"
light_purple="48;5;99"
dark_teal="48;5;23"
teal="48;5;29"
light_teal="48;5;36"
dark_red="48;5;88"
red="48;5;124"
dark_orange="48;5;172"
orange="48;5;215"
light_orange="48;5;214"
dark_yellow="48;5;100"
dark_pink="48;5;162"
pink="48;5;165"
light_pink="48;5;132"



if [ "$experiment" = false ];then
    folders="$(find "$input"/* -maxdepth 0 -type d)"
    IFS=$'\n' read -d '' -ra experiments <<< "$folders"
else
    experiments=("$input/$experiment")
fi

for exp in "${experiments[@]}"; do
   jobs=()
    if [ "$job" = false ];then
        folders="$(find "$exp"/* -maxdepth 0 -type d)"
        IFS=$'\n' read -d '' -ra jobs <<< "$folders"
    else
        numbers=($(get_interval "$job"))
        first=true
        for number in ${numbers[@]};do
            if [ $first = true ];then
                jobs=("$exp/experiment_$number")
                first=false
            else
                jobs=("${jobs[@]}" "$exp/experiment_$number")
            fi
        done
    fi
    for j in "${jobs[@]}";do
        ids=()
        if [ "$id" = false ];then
            folders="$(find "$j"/* -maxdepth 0 -type d)"
            IFS=$'\n' read -d '' -ra ids <<< "$folders"
        else
            numbers=($(get_interval "$id"))
            first=true
            for number in ${numbers[@]};do
                if [ $first = true ];then
                    ids=("$j/id_$number")
                    first=false
                else
                    ids=("${ids[@]}" "$j/id_$number")
                fi
            done
        fi
        for i in "${ids[@]}";do
            runs=()
            if [ "$run" = false ];then
                folders="$(find "$i"/* -maxdepth 0 -type d)"
                IFS=$'\n' read -d '' -ra runs <<< "$folders"
            else

                numbers=($(get_interval "$run"))
                first=true
                for number in ${numbers[@]};do
                    if [ $first = true ];then
                        runs=("$i/Run_$number")
                        first=false
                    else
                        runs=("${runs[@]}" "$i/Run_$number")
                    fi
                done


            fi
            for r in "${runs[@]}";do
                lines="`tail -n $before "$r/output/expe-out/out_extra_info.csv" 2>/dev/null`"
                runOutput=`echo $r | sed "s@$input_dir/$input_base@@g"`
                line_count=$(wc -l "$r/output/expe-out/out_extra_info.csv" 2>/dev/null | awk '{print $1}')
                
                if ! test -f "$r/output/expe-out/out_extra_info.csv" ;then
                    echo -e "...${runOutput}:   \\033[${grey}m************************************************* Error No File *************************************************\\033[0m"
                    continue
                elif [[ $line_count == 1 ]];then
                    echo -e "...${runOutput}:   \\033[${grey}m************************************************* Error No Data *************************************************\\033[0m"
                    continue
                else
                    format=""
                fi
                IFS=$'\n' read -d '' -ra entries <<< "$lines"

                
                myOutput="...$runOutput:   "
                if [ $head = true ];then
                    myHead="`head -n 2 "$r/output/expe-out/out_extra_info.csv" | tail -n 1 `"
                    entries=("$myHead" "${entries[@]}")
                fi
                if [ ${#entries[@]} -gt 1 ];then
                        echo "$myOutput"
                fi
                
                for entry in "${entries[@]}";do

                    if [ ${#entries[@]} -gt 1 ];then
                        myOutput="\t"
                        format=""
                    fi
                    print_output

                        
                done
            done
        done
    done
done
echo -e "\nFormat: $format"