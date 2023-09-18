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

function print_output()
{
    if [ $all = true ];then
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

        color=$color1
        format="$format|\\033[${color}mactually_completed_jobs\\033[0m"
        number=$(echo "$entry" |awk -F, '{printf("%'"'"'d",$1)}')
        myOutput="$myOutput|\\033[${color}m$number\\033[0m"
        color=$color2
        format="$format|\\033[${color}mnb_jobs\\033[0m"
        number=$(echo "$entry" |awk -F, '{printf("%'"'"'d",$2)}')
        myOutput="$myOutput|\\033[${color}m$number\\033[0m"
        color=$color3
        format="$format|\\033[${color}mpercent_done\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{print $3}'`\\033[0m"
        color=$color4
        format="$format|\\033[${color}mreal_time\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{print $4}'`\\033[0m"
        color=$color5
        format="$format|\\033[${color}msim_time\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{print $5}'`\\033[0m"
        color=$color6
        format="$format|\\033[${color}mqueue_size\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$6)}'`\\033[0m"
        color=$color7
        format="$format|\\033[${color}mschedule_size\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$7)}'`\\033[0m"
        color=$color8
        format="$format|\\033[${color}mnb_jobs_running\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$8)}'`\\033[0m"
        color=$color9
        format="$format|\\033[${color}mutilization\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{print $9}'`\\033[0m"
        color=$color10
        format="$format|\\033[${color}mutilization_without_resv\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{print $10}'`\\033[0m"
        color=$color11
        format="$format|\\033[${color}mnode_mem_total\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$11)}'`\\033[0m"
        color=$color12
        format="$format|\\033[${color}mnode_mem_available\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$12)}'`\\033[0m"
        color=$color13
        format="$format|\\033[${color}mbatsim_USS\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$13)}'`\\033[0m"
        color=$color14
        format="$format|\\033[${color}mbatsim_PSS\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$14)}'`\\033[0m"
        color=$color15
        format="$format|\\033[${color}mbatsim_RSS\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$15)}'`\\033[0m"
        color=$color16
        format="$format|\\033[${color}mbatsched_USS\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$16)}'`\\033[0m"
        color=$color17
        format="$format|\\033[${color}mbatsched_PSS\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$17)}'`\\033[0m"
        color=$color18
        format="$format|\\033[${color}mbatsched_RSS\\033[0m"
        myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, '{printf("%'"'"'d",$18)}'`\\033[0m"

        echo -e "$myOutput"
    else

        if [ $percent = true ];then
            color=$dark_purple
            format="$format|  \\033[${color}mpercent_done\\033[0m"
            myOutput="$myOutput  |  \\033[${color}m`echo "$entry" |awk -F, '{print $3}'`\\033[0m"
        fi
        if [ $completed = true ];then
            color=$light_blue
            format="$format |  \\033[${color}mactually_completed_jobs\\033[0m"
            number=$(echo "$entry" |awk -F, '{printf("%'"'"'d",$1)}')
            myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
        fi
        if [ $queue = true ];then
            color=$dark_green
            format="$format  |  \\033[${color}mqueue_size\\033[0m"
            number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$6)}')
            myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
        fi
        if [ $schedule = true ];then
            color=$light_purple
            format="$format  |  \\033[${color}mschedule_size\\033[0m"
            number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$7)}')
            myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
        fi
        if [ $memory != false ];then
            color1=$dark_teal
            color2=$teal
            color3=$light_teal
            color4=$dark_pink
            color5=$pink
            color6=$light_pink
            color7=$dark_grey
            color8=$light_grey
            case "$memory" in
            "both")
                format="$format  |  \\033[${color1}mbatsim_USS\\033[0m  |  \\033[${color2}mbatsim_PSS\\033[0m  |  \\033[${color3}mbatsim_RSS\\033[0m  |  \\033[${color4}mbatsched_USS\\033[0m  |  \\033[${color5}mbatsched_PSS\\033[0m  |  \\033[${color6}mbatsched_RSS\\033[0m"
                color=$color1
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$13)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color2
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$14)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color3
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$15)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color4
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$16)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color5
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$17)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color6
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$18)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                ;;
            "batsim")
                format="$format  |  \\033[${color1}mbatsim_USS\\033[0m  |  \\033[${color2}mbatsim_PSS\\033[0m  |  \\033[${color3}mbatsim_RSS\\033[0m"
                color=$color1
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$13)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color2
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$14)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color3
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$15)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                ;;
            "batsched")
                format="$format  |  \\033[${color4}mbatsched_USS  |  \\033[${color5}mbatsched_PSS\\033[0m  |  \\033[${color6}mbatsched_RSS\\033[0m"
                color=$color4
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$16)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color5
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$17)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color6
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$18)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                ;;
            "all")
                format="$format  |  \\033[${color7}mnode_mem_total\\033[0m  |  \\033[${color8}mnode_mem_available\\033[0m  |  \\033[${color1}mbatsim_USS\\033[0m  |  \\033[${color2}mbatsim_PSS\\033[0m  |  \\033[${color3}mbatsim_RSS\\033[0m  |  \\033[${color4}mbatsched_USS\\033[0m  |  \\033[${color5}mbatsched_PSS\\033[0m  |  \\033[${color6}mbatsched_RSS\\033[0m"
                color=$color7
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$11)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color8
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$12)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color1
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$13)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color2
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$14)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color3
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$15)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color4
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$16)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color5
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$17)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color6
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$18)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                ;;
            "available")
                format="$format  |  \\033[${color7}mnode_mem_total  |  \\033[${color8}mnode_mem_available\\033[0m"
                color=$color7
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$11)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
                color=$color8
                number=$(echo "$entry" | awk -F, '{printf("%'"'"'d",$12)}')
                myOutput="$myOutput  |  \\033[${color}m$number\\033[0m"
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

VALID_ARGS=$(getopt -o i:apcm:qsd:r:e:j:b:H --long input:,all,percent,completed,memory:,queue-size,schedule-size,experiment:,job:,id:,run:,before:,head,help -- "$@")
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
memory=false
queue=false
schedule=false
before=1
all=false
head=false


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
        shift 1
        ;;
    -p | --percent)
        echo "p"
        percent=true
        shift 1
        ;;
    -c | --completed)
        echo "c"
        completed=true
        shift 1
        ;;
    -m | --memory)
        echo "m $2"
        memory="$2"
        shift 2
        ;;
    -q | --queue-size)
        echo "q"
        queue=true
        shift 1
        ;;
    -s | --schedule-size)
        echo "s"
        schedule=true
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
    progress.sh -i <folder> [-e <folder>] [-j <array string>] [-d <array string>] [-r <array string>] [-b <int>] [-p] [-c] [-q] [-s] [-m <batsim|batsched|both|all|available>] [--head]

Required Options:
    -i, --input <folder>           Where the experiments are.  This is supposed to be the outer folder passed to ./myBatchTasks.sh
                                   If it has a forward slash '/' in the name it will assume it is an absolute path.
                                   If it does not have a forward slash '/' in the name it will assume it is located in "$prefix/experiments/<input>"
Optional Options:

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

    -b, --before <int>             The amount of entries, starting from the last one, to include

    -H, --head                     Print the first entry in the out_extra_info.csv file first ( possilbe use is to check on how long the sim has been going )

    -a, --all                      Print out all data in the entry

    -p, --percent                  Include the percentage done that the sim has done

    -c, --completed                Include the amount of ACTUALLY completed jobs and TOTAL jobs in output
    
    -q, --queue-size               Include the queue-size in output

    -s, --schedule-size            Include the schedule-size in output

    -m, --memory <string>          Include the memory usage.  Will include the USS,PSS,RSS for "batsim|batsched|both".  Other options are "all|available"

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
                runOutput=`echo $r | sed "s@$input_dir@@g"`
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
