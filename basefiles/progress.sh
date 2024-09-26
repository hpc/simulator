#!/usr/bin/bash
if [ -f ~/.dirB.sh ];then
    source ~/.dirB.sh
fi
cols=`tput cols`
max_cols=$(( cols - 10 ))
if [ $max_cols -lt 30 ];then
    echo "Error, make your terminal wider"
    exit
fi

function break_format()
{
    old_tab="$tab"
    tab="\t"
    format_max_cols=$(( cols - 10 ))
    if [ $superCondensed = true ];then
        format_max_cols=$max_cols
        tab="$old_tab"
    fi
    return_string=""
    displaySize=`echo -e "$format" | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' | wc -c`
    if [ $displaySize -lt $format_max_cols ];then
        final_string="$format"
        finalA=(${final_string//|/ })
        counts=(${#finalA[@]})
    else
        bf_count=0
        counts=()
        final_string=""
        line_string=""
        tmp_string=""
        strA=(${format//|/ })
        strACount=${#strA[@]}
        #now we have each label in the array
        for i in ${strA[@]};do
            #add i to tmp_string
            tmp_string="$tmp_string|$i"
            #the displaySize should be without color codes
            displaySize=`echo -e "$tmp_string" | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' | wc -c`
            if [ $displaySize -lt $format_max_cols ];then
                line_string="$tmp_string"
                bf_count=$(( bf_count + 1 ))
            else
                    
                if [[ $bf_count -eq 0 ]];then
                    #ok the format key is never going to fit, fit it anyway
                    line_string="$tmp_string"
                    bf_count=1
                fi
                #record how many got in the line
                counts+=($bf_count)
                bf_count=1
                #the displaySize goes over the max_cols
                #start the tmp_string over
                tmp_string="|$i"
                #line string can be moved to final_string
                if [[ $final_string == "" ]];then
                    final_string="$line_string"
                else
                    final_string="$final_string\n$tab$line_string"
                fi
                line_string="$tmp_string"
            fi
        done
        if [[ $line_string != "" ]];then
            final_string="$final_string\n$tab$line_string"
            counts+=($bf_count)
        elif [[ $tmp_string != "" ]];then
            final_string="$final_string\n$tab$tmp_string"
            counts+=(1)
        fi

    fi
    tab=$old_tab
    return_values=("$final_string")
    return_values+=($strACount)
    return_values+=(${counts[@]})
}

function break_output()
{
    col_diff=10
    output_max_cols=$(( cols - $col_diff ))
    displaySize=`echo -e "$myOutput" | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' | wc -c`
    if [ $displaySize -lt $output_max_cols ];then
        final_string="$myOutput"
    else
        final_string=""
        line_string=""
        tmp_string="$tab"
        OLD_IFS=$IFS
        IFS="|"
        strA=($myOutput)
        #strA=($(echo $myOutput | awk 'BEGIN{FS="|"}{for(i=2;i<=NF;i++)printf "'\''%s'\'' ", $i}'))

        #strA=(${myOutput/// })
        #now we have each label in the array
        if [ $tryOneliner = true ];then
            start=1
            tmp_string=${strA[0]}
        fi
        for i in ${strA[@]:1};do
            #add i to tmp_string
            #if [ $first = true ];then
            #    first=false
            #    continue
            #fi
            tmp_string="$tmp_string|$i"
            #the displaySize should be without color codes
            displaySize=`echo -e "$tmp_string" | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' | wc -c`
            if [ $displaySize -lt $output_max_cols ];then
                line_string="$tmp_string"
            else
                #the displaySize goes over the max_cols
                #start the tmp_string over
                tmp_string="|$i"
                #line string can be moved to final_string
                if [[ $final_string == "" ]];then
                    final_string="$line_string"
                else
                    final_string="$final_string\n$tab$line_string"
                fi
                line_string=""
            fi
        done
        IFS=$OLD_IFS
        if [[ $line_string != "" ]];then
            final_string="$final_string\n$tab$line_string"
        elif [[ $tmp_string != "" ]];then
            final_string="$final_string\n$tab$tmp_string"
        fi
    fi
    myOutput="$final_string"
}
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
            grep ":"<<<$i > /dev/null
            if [ $? -eq 0 ];then
                IFS=: read start end step<<<"$i"
                mySequence=`seq $start $step $end`
                numbers=(${numbers[*]} ${mySequence[*]})
            else
                numbers=(${numbers[*]} $i)
            fi
        fi
    done
    echo "${numbers[*]}"
}
subtract_output_count()
{
    if [ $condensed = true ] || [ $superCondensed = true ];then
        output_count=1000
    fi
    output_count=$(( output_count -1 ))
    if [ $output_count -eq 0 ];then
        #ok the output count is down to 0
        #we need a new output count and iterator
        count_iter=$(( count_iter + 1 ))
        if [ ${#return_values[@]} -gt $count_iter ];then
            #ok we can add the newline
            myOutput="$myOutput\n$output_tab"
            #ok we can get the count
            output_count=${return_values[$count_iter]}
        else
            output_count=1000 #should handle all of the rest
        fi
    fi
}
print_mem_f()
{
    if [ $superCondensed = true ];then
        name=$alt_name
    fi
    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
}
print_mem()
{
    #tmp_format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #if [ ${#tmp_format} -gt $cols ];then
    #    list_of_formats+=($format)
    #    format=""
    #    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #fi


    if [[ $divideBy == -1 ]];then
            myOutput="$myOutput|\\033[${color}m`echo "$entry" \
            | awk -F, -v field=$field '{num=$field;if (num>2^30){div=2^30;u="TiB"}else if (num>2^20){div=2^20;u="GiB"}else if (num>2^10){div=2^10;u="MiB"}else{div=1;u="KiB"};num=int(num/div) ;printf("%'"'"'d %s",num,u)}'`\\033[0m"
    else
            myOutput="$myOutput|\\033[${color}m`echo "$entry" |awk -F, -v field=$field -v div=$divideBy -v u=$memSize '{num=($field/div);num=int(num);printf("%'"'"'d %s",num,u)}'`\\033[0m"
    fi
    subtract_output_count

}
print_number_f()
{
    if [ $superCondensed = true ];then
        name=$alt_name
    fi
    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
}
print_number()
{
    #tmp_format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #if [ ${#tmp_format} -gt $cols ];then
    #    list_of_formats+=($format)
    #    format=""
    #    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #fi
    number=$(echo "$entry" |awk -F, -v field=$field '{printf("%'"'"'d",$field)}')
    myOutput="$myOutput|\\033[${color}m$number\\033[0m"
    subtract_output_count
}
print_percent_f()
{
    if [ $superCondensed = true ];then
        name=$alt_name
    fi
    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
}
print_percent()
{
    #tmp_format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #if [ ${#tmp_format} -gt $cols ];then
    #    list_of_formats+=($format)
    #    format=""
    #    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #fi
    number=$(echo "$entry" |awk -F, -v field=$field '{x=$field;printf("%'"'"'d",x*100)}')
    myOutput="$myOutput|\\033[${color}m$number\\033[0m"
    subtract_output_count
}
print_entry_f()
{
    if [ $superCondensed = true ];then
        name=$alt_name
    fi
    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
}
print_entry()
{
    #tmp_format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #if [ ${#tmp_format} -gt $cols ];then
    #    list_of_formats+=($format)
    #    format=""
    #    format="${format}${space}|${space}\\033[${color}m${name}\\033[0m"
    #fi
    number=$(echo "$entry" |awk -F, -v field=$field '{printf("%s",$field)}')
    myOutput="$myOutput|\\033[${color}m$number\\033[0m"
    subtract_output_count
}


completed_jobs_f()
{
    color=$color1; field=1; name="actually_completed_jobs";alt_name="comp_jobs";
    print_number_f;
    color=$color2; field=2; name="nb_jobs"; alt_name="jobs";
    print_number_f;
}
completed_jobs()
{
    color=$color1; field=1; name="actually_completed_jobs"; print_number;
    color=$color2; field=2; name="nb_jobs"; print_number;
}

percent_done_f()
{
    color=$color3; field=3; name="percent_done"; alt_name="%_done";
    print_entry_f;
    if [ $overallPercent = true ];then
        color=$color23; field=23;name="overall_percent";alt_name="all_%";
        print_entry_f;
    fi
}
percent_done()
{
    color=$color3; field=3; name="percent_done"; print_entry;
    if [ $overallPercent = true ];then
        color=$color23; field=23;name="overall_percent";print_entry;
    fi
}
original_info_f()
{
    color=$color21;field=21;name="total_completed_jobs";alt_name="tot_comp";
    print_number_f;
    color=$color20;field=20;name="nb_orig_jobs";alt_name="o_jobs";
    print_number_f;
    color=$color22;field=22;name="nb_resubmit";alt_name="nb_re";
    print_number_f;
}
original_info()
{
    color=$color21;field=21;name="total_completed_jobs";alt_name="tot_comp";
    print_number;
    color=$color20;field=20;name="nb_orig_jobs";alt_name="o_jobs";
    print_number;
    color=$color22;field=22;name="nb_resubmit";alt_name="nb_re";
    print_number;
}

elapsed_f()
{
    color=$color19; field=19; name="elapsed_time"; alt_name="el_time";
    print_entry_f;
    
}
elapsed()
{
    color=$color19; field=19; name="elapsed_time"; alt_name="el_time";
    print_entry;
}
times_f()
{
    color=$color4; field=4; name="real_time"; alt_name="rl_time";
    print_entry_f;
    color=$color5; field=5; name="sim_time"; alt_name="sm_time"
    print_entry_f; 
}
times()
{
    color=$color4; field=4; name="real_time"; print_entry;
    color=$color5; field=5; name="sim_time"; print_entry;
}
queue_size_f()
{
    color=$color6; field=6; name="queue_size"; alt_name="q_sz";
    print_number_f;
}
queue_size()
{
    color=$color6; field=6; name="queue_size"; print_number;
}
schedule_size_f()
{
    color=$color7; field=7; name="schedule_size"; alt_name="sched_sz";
    print_number_f;
}
schedule_size()
{
    color=$color7; field=7; name="schedule_size"; print_number;
}
schedule_info_f()
{
    queue_size_f
    schedule_size_f
    color=$color8; field=8; name="nb_jobs_running"; alt_name="nb_run";
    print_number_f;
}
schedule_info()
{
    queue_size
    schedule_size
    color=$color8; field=8; name="nb_jobs_running"; print_number;
}
utilization_f()
{
    color=$color9; field=9; name="utilization"; alt_name="util";
    print_percent_f;
    color=$color10; field=10; name="utilization_no_resv"; alt_name="util_no_r";
    print_percent_f;
}
utilization()
{
    color=$color9; field=9; name="utilization"; print_percent;
    color=$color10; field=10; name="utilization_no_resv"; print_percent;
}
mem_avail_f()
{

    color=$color11; field=11; name="node_mem_total"; alt_name="tot_mem";
    print_mem_f;
    color=$color12; field=12; name="node_mem_avail"; alt_name="avail_mem";
    print_mem_f;

}
mem_avail()
{

    color=$color11; field=11; name="node_mem_total"; print_mem;
    color=$color12; field=12; name="node_mem_avail"; print_mem;

}

mem_batsim_f()
{
    color=$color13; field=13; name="batsim_USS"; alt_name="bat_USS";
    print_mem_f;
    color=$color14; field=14; name="batsim_PSS"; alt_name="bat_PSS";
    print_mem_f;
    color=$color15; field=15; name="batsim_RSS"; alt_name="bat_RSS";
    print_mem_f;
}
mem_batsim()
{
    color=$color13; field=13; name="batsim_USS"; print_mem;
    color=$color14; field=14; name="batsim_PSS"; print_mem;
    color=$color15; field=15; name="batsim_RSS"; print_mem;
}
mem_batsched_f()
{
    color=$color16; field=16; name="batsched_USS"; alt_name="sched_USS";
    print_mem_f;
    color=$color17; field=17; name="batsched_PSS"; alt_name="sched_PSS";
    print_mem_f;
    color=$color18; field=18; name="batsched_RSS"; alt_name="sched_RSS";
    print_mem_f;
}
mem_batsched()
{
    color=$color16; field=16; name="batsched_USS"; print_mem;
    color=$color17; field=17; name="batsched_PSS"; print_mem;
    color=$color18; field=18; name="batsched_RSS"; print_mem;
}



function setup_output()
{

    color1=$act_comp_jobs_light_blue
    color2=$nb_jobs_gold
    color3=$percent_dark_purple
    color4=$real_time_blue
    color5=$sim_time_dark_red
    color6=$queue_dark_green
    color7=$sched_sz_light_purple
    color8=$job_run_green
    color9=$util_dark_yellow
    color10=$util_no_r_dark_orange
    color11=$tot_mem_dark_grey
    color12=$avail_mem_light_grey
    color13=$bat_uss_dark_teal
    color14=$bat_pss_teal
    color15=$bat_rss_light_teal
    color16=$sched_uss_dark_pink
    color17=$sched_pss_pink
    color18=$sched_rss_light_pink
    color19=$elapsed_darker_blue
    color20=$tot_orig_jobs_gold
    color21=$tot_comp_blue
    color22=$resubmit_red
    color23=$overall_p_darker_purple
    space=""
    noAll=false
    if [ $noInfo != false ];then
        echo "${noInfo[*]}" | grep "a" >/dev/null 2>&1
        if [ $? -eq 0 ];then
            noAll=true
        fi
        if [ $print = false ] && [ $noAll = false ];then
            completed=true;percent=true;timeO=true;
            scheduleInfo=true;queue=true;schedule=true;
            utilization=true;memory="all";print=true
        fi
        for command in ${noInfo[@]};do
            case $command in

                c)  completed=false
                    ;;
                p)  percent=false
                    ;;
                t)  timeO=false
                    ;;
                S)  scheduleInfo=false
                    queue=false
                    schedule=false
                    ;;
                q)  queue=false
                    ;;
                s)  schedule=false
                    ;;
                u)  utilization=false
                    ;;
                m)  memory=false
                    ;;
                a)  noAll=true
                    ;;
            esac
        done
    fi
    if ([ $all = true ] || [ $print = false ]) && [ $noAll = false ];then
        space=""
        completed=true;percent=true;timeO=true;
        scheduleInfo=true;queue=true;schedule=true;
        utilization=true;memory="all"
    fi




    output_commands=()

    if [ $completed = true ];then
        output_commands+=('completed_jobs')
    fi
    if [ $percent = true ];then
        output_commands+=('percent_done')
    fi
    if [ $original_info = true ];then
        output_commands+=('original_info')
    fi
    if [ $timeO = true ];then
        output_commands+=('times')
    fi
    if [ $elapsedTime = true ];then
        output_commands+=('elapsed')
    fi
    if [ $scheduleInfo = true ];then
        output_commands+=('schedule_info')
    elif [ $queue = true ];then
        output_commands+=('queue_size')
        if [ $schedule = true ];then
            output_commands+=('schedule_size')
        fi
    elif [ $schedule = true ];then
        output_commands+=('schedule_size')
    fi
    if [ $utilization = true ];then
        output_commands+=('utilization')
    fi
    if [ $memory != false ];then


        case "$memory" in
        "both")
            output_commands+=('mem_batsim')
            output_commands+=('mem_batsched')
            ;;
        "batsim")
            output_commands+=('mem_batsim')
            ;;
        "batsched")
            output_commands+=('mem_batsched')
            ;;
        "all")
            output_commands+=('mem_avail')
            output_commands+=('mem_batsim')
            output_commands+=('mem_batsched')
            ;;
        "available")
            output_commands+=('mem_avail')
            ;;
        esac
    fi
    return_values=()
    for i in ${output_commands[@]};do
        ${i}_f
    done
    break_format
    endingFormat=${return_values[0]}
    saved_myOutput="$myOutput"
    #count_iter=2
    #output_count=${return_values[$count_iter]}
    for i in ${output_commands[@]};do
        $i
    done
    displaySize=`echo -e "$myOutput" | sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g' | wc -c`
    onelinerMaxCols=$(( cols - 15 ))
    if [ $displaySize -lt $onelinerMaxCols ];then
        tryOneliner=true
    fi
    myOutput="$saved_myOutput"
}
function print_output()
{

    #so we have all the commands, run them with just the format option first

    #now we have the format, run the commands
    count_iter=2
    output_count=${return_values[$count_iter]}
    for i in ${output_commands[@]};do
        $i
    done
    if [ $condensed = true ] || [ $superCondensed = true ];then
        break_output
    fi
    echo -e "$myOutput"

}
function get_input_variable
{
        isRun=1;isOutput=1;isOut=1;
        myString="$1"
        grep "/" <<<"$myString" > /dev/null
        if [ $? -eq 0 ];then
            #it's an absolute path
            input="$1"
            input_dir=$(dirname "$1")
            input_base=$(basename "$1")
            #now check if we are at an id_#/ or experiment_#
            grep "id_" <<<"$input_base" > /dev/null
            isId=$?
            grep "experiment_" <<<"$input_base" > /dev/null
            isExp=$?
            if [ $isId -eq 0 ] || [ $isExp -eq 0 ];then
                if [ $isId -eq 0 ];then
                    up=3
                elif [ $isExp -eq 0 ];then
                    up=2
                fi
                for i in `seq 1 1 $up`;do
                    input_base=$(basename $input_dir)
                    input_dir=$(dirname $input_dir)
                done
                input="$input_dir/$input_base"
            fi
            #now check if we are at a Run_#/ or output/ or expe-out/
            #this would make it clear what progress we were after
            grep "Run_" <<<"$input_base" > /dev/null
            isRun=$?
            grep "output" <<<"$input_base" > /dev/null
            isOutput=$?
            grep "expe-out"<<<"$input_base" > /dev/null
            isOut=$?
            if [ $isRun -eq 0 ] || [ $isOutput -eq 0 ] || [ $isOut -eq 0 ];then
                computedInput=true
                if [ $isOut -eq 0 ];then
                    up=2
                elif [ $isOutput -eq 0 ];then
                    up=1
                else
                    up=0
                fi
                for i in `seq 1 1 $up`;do
                    input_base=$(basename $input_dir)
                    input_dir=$(dirname $input_dir)
                done
                #so now we are all at Run_1, input_base=Run_1, input_dir=.../id_1
                run=`echo $input_base | sed 's@Run_@@g'`
                input_base=$(basename $input_dir)
                input_dir=$(dirname $input_dir)
                id=`echo $input_base | sed 's@id_@@g'`
                input_base=$(basename $input_dir)
                input_dir=$(dirname $input_dir)
                job=`echo $input_base | sed 's@experiment_@@g'`
                input_base=$(basename $input_dir)
                input_dir=$(dirname $input_dir)
                experiment=$input_base
                input=$input_dir
                input_base=$(basename $input_dir)
                input_dir=$(dirname $input_dir)
                #so now we are up to the project folder like usual 
                #but now run is set, id is set, job is set, and experiment is set
            fi
        else
            input_dir="$prefix/experiments"
            input_base="$1"
            input="$input_dir/$input_base"
        fi
}


MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
export prefix="$(cd -- "$MY_PATH"/../ && pwd)"

source $prefix/basefiles/batsim_environment.sh
export basefiles=$prefix/basefiles
source $prefix/python_env/bin/activate

VALID_ARGS=$(getopt -o i:aEOopcm:qsNI:r:e:j:b:HM:tSuUFT:hP:123456789d:CZz: --long up,normal-info,no-info:,original-info,condensed,super-condensed,elapsed-time,overall-percent,input:,prompt:,all,percent,completed,time,memory:,memory-size:,schedule-info,utilization,queue-size,schedule-size,experiment:,job:,id:,run:,finished-sims,unfinished-sims,threshold:,before:,head,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi
input=false
experiment=false;e_set=false;
job=false;j_set=false;
id=false;i_set=false;
run=false;r_set=false;
finished=false
unfinished=false
threshold=(false 0)
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
divideBy=-1
print=false
options=""
prompt="None"
overallPercent=false
elapsedTime=false
condensed=false
superCondensed=false
original_info=false
noInfo=false
normalInfo=false
up=false

eval set -- "$VALID_ARGS"
while true; do
  case "$1" in
    -[1-9])
        folder="folder${1:1}"
        get_input_variable ${!folder}
        shift 1
        ;;
    -d)
       get_input_variable $(d $2)
       shift 2
       ;;
    -i | --input)
        options="$options, i $2"
        get_input_variable $2
        shift 2
        ;;
    -P | --prompt)
        options="$options, P $2"
        prompt="$2"
        shift 2
        ;;
    --up)
        options="$options, up"
        up=true
        shift 1
        ;;
     -e | --experiment)
        options="$options, e $2"
        e_set=true
        experiment="$2"
        shift 2
        ;;
    -j | --job)
        options="$options, j $2"
        j_set=true
        job="$2"
        shift 2
        ;;
    -I | --id)
        options="$options, id $2"
        i_set=true
        id="$2"
        shift 2
        ;;
    -r | --run)
        options="$options, r $2"
        r_set=true
        run="$2"
        shift 2
        ;;
    -F | --finished-sims)
        options="$options, F"
        finished=true
        shift 1
        ;;
    -U | --unfinished-sims)
        options="$options, U"
        unfinished=true
        shift 1
        ;;
    -T | --threshold)
        options="$options, T $2"
        read -ra threshold <<<"$2"
        shift 2
        ;;
    -a | --all)
        options="$options, a"
        all=true
        print=true
        shift 1
        ;;
    -N | --normal-info)
        options="$options, a"
        normalInfo=true
        print=true
        shift 1
        ;;
    -o | --overall-percent)
        options="$options, o"
        overallPercent=true
        shift 1
        ;;
    -O | --original-info)
        options="$options, O"
        original_info=true
        overallPercent=true
        shift 1
        ;;
    -z | --no-info)
        options="$options, z"
        read -ra noInfo <<<"$2"
        shift 2
        ;;
    -E | --elapsed-time)
        options="$options, E"
        elapsedTime=true
        shift 1
        ;;
    -p | --percent)
        options="$options, p"
        percent=true
        print=true
        shift 1
        ;;
    -c | --completed)
        options="$options, c"
        completed=true
        print=true
        shift 1
        ;;
    -t | --time)
        options="$options, t"
        timeO=true
        print=true
        shift 1
        ;;
    -m | --memory)
        options="$options, m $2"
        print=true
        memory="$2"
        shift 2
        ;;
    -M | --memory-size)
        options="$options, M $2"
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
        options="$options, S"
        print=true
        scheduleInfo=true
        shift 1
        ;;
    -q | --queue-size)
        options="$options, q"
        print=true
        queue=true
        shift 1
        ;;
    -s | --schedule-size)
        options="$options, s"
        print=true
        schedule=true
        shift 1
        ;;
    -u | --utilization)
        options="$options, u"
        print=true
        utilization=true
        shift 1
        ;;
    -b | --before)
        options="$options, b $2"
        before=$2
        shift 2
        ;;
    -H | --head)
        options="$options, head"
        head=true
        shift 1
        ;;
    -C | --condensed)
        options="$options, C"
        condensed=true
        #max_cols=$(( cols + 200 ))
        shift 1
        ;;
    -Z | --super-condensed)
        options="$options, Z"
        condensed=false
        superCondensed=true
        #max_cols=$(( cols + 200 ))
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
if [ $input = false ] && [[ $prompt == "None" ]];then
cat <<"EOF"

progress.sh: used to show the progress of all simulations in a folder, or just certain ones, with options for what to show.

Usage:
    progress.sh [-# | -i <folder> | -d <bookmark> ] [-P <options>] [-e <folder>] [-j <array string>] [-D <array string>] [-r <array string>] [--up]
                            [-b <int>] [-H] [-E] [-O] [-N] [-p] [-o] [-c] [-q] [-s] [-m <batsim|batsched|both|all|available>] [-M K|M|G|T|H] [-z "<opts>"]
                            [-C] [-Z]  

Mostly Required Options:
    -#                             Will use the environment variable folder# for input.  It will act as if you used -i ${folder#}
                                   This is best used in conjunction with batFolder
                                   NOTE: using this method requires folder# to be exported: export folder#
                                   NOTE: batFolder automatically exports the corresponding folder# variable

    -d <bookmark>                  Will use the dibB.sh bookmark

    -i, --input <folder>           Where the experiments are.  This is supposed to be the outer folder passed to ./myBatchTasks.sh
                                   If it has a forward slash '/' in the name it will assume it is an absolute path.
                                   If it does not have a forward slash '/' in the name it will assume it is located in "$prefix/experiments/<input>"
                                   If --prompt is used, this folder is interpreted as where to look for experiment directories.
                                   If --prompt is used and this option is omitted, the default will be used '${prefix}/experiments'

Optional Options:

Folder Options:
    -P, --prompt <options>         Another option instead of setting input directly
                                   Will go into folder '--input <folder>' and list the directories for you.  Select the folder you are after with a number
                                   If --input is omitted, will use '${prefix}/experiments'
                                   The options you want to send ls comes after prompt, but use quotes around the whole list of options as to not confuse this script
                                   Make sure you use empty quotes if not setting any options
                                   Also look into using batFolder for repeated uses of progress.sh
                                   example:    progress.sh -P '-ltr'    or      progress.sh -i "/some/other/path" -P ''

    --up                           Normally if you pass input as a Run_#,output,or expe-out folder you will get a single progress of that folder's simulation
                                   With this option, it will always set the corresponding project folder as the input.  Must appear after -i option
Which-Simulation Options:

    -e, --experiment <folder>      If you want to focus on just one experiment (in the sense of config files where there was an input and output json for each experiment)
                                   then use this to enter the folder.  The path retrieved will then be ".../<input>/<experiment>/*"
                                   <folder> can include wildcard (*) characters as well. For instance...
                                        progress.sh -i ${folder1} -e "*shuffled*"
                                        if you were going to shuffle some experiments and named those experiments with 'shuffled' in the name,
                                        then this would get you all the experiments with the word 'shuffled' in it.

    -j, --job <array string>       If you want to focus on just one job (in the sense of folders named experiment_#) then use this to enter the folder number.
                                   If used with --experiment then it will retrieve paths ".../<input>/<experiment>/experiment_<job>/*
                                   If not used with --experiment, then it will retrieve paths ".../<input>/*/experiment_<job>/*
                                   If multiple jobs are wanted then put the job numbers into a string, for example:
                                   '-j "1 2-5 10"'  will gather experiment_1,experiment_2,experiment_3,experiment_4,experiment_5, and experiment_10
                                   '-j "3:1000:50 1 1050-1055"' will gather '3-1000 step of 50', '1' and '1050,1051,1052,1053,1054,1055'

    -I, --id <array string>        If you want to focus on just one id (in the sense of folders named id_#) then use this to enter the folder number.
                                   Basically the same as --job as far as how it works, except we focus on the id(s)
                                   Look at --job for string format

    -r, --run <array string>       If you want to focus on just one run (in the sense of folders named Run_#) then use this to enter the folder number.
                                   Basically the same as --job and --id as far as how it works, except we focus on the run(s)
                                   Look at --job for string format

    -F, --finished-sims            Only include sims that have overall_jobs_completed == overall_jobs

    -U, --unfinished-sims          Only include sims that have overall_jobs_completed != overall_jobs

    -T, --threshold <string>       Only include sims that are above or below a threshold for overall_percent_done
                                   format of string: "(+|-) <threshold float>"

What-Info Options:

    -b, --before <int>             The amount of entries, starting from the last one, to include

    -H, --head                     Print the first entry in the out_extra_info.csv file first ( possible use is to check on how long the sim has been going )

    -a, --all                      Print out all data in the entry except elapsed-time and overall-percent.  Default if nothing else is chosen to print.

    -E, --elapsed-time             Prints out the real elapsed time of the simulation.  Must include the option to see it.
                                   Not included in the --all option, but keeps --all the default.
                                   Use -z "a" option to supress all, or choose what else to print out.

    -o, --overall-percent          Prints out the overall-percent when used with checkpoints.  Must include the option to see it.
                                   Not included in the --all option, but keeps --all the default.
                                   Use -z "a" option to supress all, or choose what else to print out.

    -O, --original-info            Prints out "overall-percent, original-jobs,number-resubmits,total-actually-completed"
                                   Not included in the --all option, but keeps --all the default.
                                   Use -z "a" option to supress all, or choose what else to print out.

    -p, --percent                  Include the percentage done that the sim has done

    -c, --completed                Include the amount of ACTUALLY completed jobs and TOTAL jobs

    -t, --time                     Include the real-time and sim-time

    -S, --schedule-info            Include queue-size,schedule-size,nb-jobs-running

    -q, --queue-size               Include the queue-size in output

    -s, --schedule-size            Include the schedule-size in output

    -u, --utilization              Include utilization and utilization-without-reservations

    -m, --memory <string>          Include the memory usage.  Will include the USS,PSS,RSS for "batsim|batsched|both".  Other options are "all|available"

    -M, --memory-size <string>     When displaying memory, what size to display: KB | MB | GB | TB | H.  Single letter is fine too:  K | M | G | T | H
                                   This will actually be in KiB, MiB, GiB, or TiB
                                   H signifies you want human-readable units.  This is the largest unit that makes sense for the data.
                                   [default: H]

    -z, --no-info <string>         What categories NOT to show.<string> is a comma seperated string with all of the short options above
                                   but instead of displaying what the options would normally select, it displays everything except them.
                                   ex: "t m" no time, no memory, everything else
                                   ex: "a" nothing else except what is selected (use with -O and -o options)
    -N, --normal-info              Prints a normal usage scenario: -O -E -c -p -Z
Presentation Options
    -C, --condensed                When displaying data, will not follow the line breaks of the "format" at the bottom

    -Z, --super-condensed          When displaying format at the bottom, will use abbreviated names
                                   When displaying data, will not follow the line breaks of the "format" string
                                   TODO when displaying path, will use a condensed version of it


    -h, --help                     Display this usage page

EOF
exit
fi
if [ $up = true ];then
    if [ $e_set = false ];then
        experiment=false
    fi
    if [ $j_set = false ];then
        job=false
    fi
    if [ $i_set = false ];then
        id=false
    fi
    if [ $r_set = false ];then
        run=false
    fi
fi
if [ $normalInfo = true ];then
    original_info=true #O
    overallPercent=true #O
    elapsedTime=true #E
    completed=true #c
    percent=true #p
    condensed=false #Z
    superCondensed=true #Z
fi
#echo "options: $options"
black="48;5;16"
act_comp_jobs_light_blue="48;5;33"  #field 1
nb_jobs_gold="48;5;94"              #field 2
percent_dark_purple="48;5;56"       #field 3
overall_p_darker_purple="48;5;54"   #field 23
tot_comp_blue="48;5;31"             #field 21
tot_orig_jobs_gold="48;5;101"       #field 20
resubmit_red="48;5;160"             #field 22
real_time_blue="48;5;21"            #field 4
sim_time_dark_red="48;5;88"         #field 5
elapsed_darker_blue="48;5;18"       #field 19
queue_dark_green="48;5;22"          #field 6
sched_sz_light_purple="48;5;99"     #field 7
job_run_green="48;5;28"             #field 8
util_dark_yellow="48;5;100"         #field 9
util_no_r_dark_orange="48;5;172"    #field 10
tot_mem_dark_grey="48;5;235"        #field 11
avail_mem_light_grey="48;5;243"     #field 12
bat_uss_dark_teal="48;5;23"         #field 13
bat_pss_teal="48;5;29"              #field 14
bat_rss_light_teal="48;5;36"        #field 15
sched_uss_dark_pink="48;5;162"      #field 16
sched_pss_pink="48;5;165"           #field 17
sched_rss_light_pink="48;5;132"     #field 18


grey="48;5;238"
dark_blue="48;5;17"
light_green="48;5;34"
purple="48;5;57"
red="48;5;124"
orange="48;5;215"
light_orange="48;5;214"


endingFormat="false"
setup=true
tryOneliner=false
dots=".../"
if [ $superCondensed = true ];then
    dots=""
fi
expandPath() {
  echo $(cd $1;pwd)
}
echo "folder: $input"
function progressBatFolder
{
    path=`expandPath $1`
    enter=false
    /usr/bin/ls $2 -d "$path"/*/ | sed "s#[/].*[/]\(.*\)/#\1#g" | nl
    folders="`/usr/bin/ls $2 -d "$path"/*/ | sed "s#[/].*[/]\(.*\)/#\1#g" | nl`"
    IFS=$'\n' read -d '' -ra foldersArray <<< "$folders"
    printf " \\033[48;5;23;38;5;16;1mPrepend selection with a '.' (period) to enter directory\\033[0m\n "
    printf "\\033[48;5;23;38;5;16;1mEnter a choice (0 to exit):\\033[0m "
    read choice
    if [[ ${choice:0:1} == "." ]];then
        enter=true
        choice=${choice:1}
    fi
    choice=`echo $choice | awk '{num=$1-1;print num}'`
    if [[ $choice == -1 ]];then
        exit
    fi

    input_dir="${input}"
    input_base="${foldersArray[$choice]}"
    input_base="`echo "$input_base" | awk '{print $NF}'`"
    input="$input_dir/$input_base"
    #printf -v "folder${num}" '%s' "$input_dir/$input_base"
    if [ $enter = true ];then

        progressBatFolder "$input_dir/$input_base" $2

    fi
}

if [[ $prompt != "None" ]];then
    if [ $input = false ];then
        input="$prefix/experiments"
    fi
    progressBatFolder $input $prompt
fi


if [ "$experiment" = false ];then
    folders="$(find "$input"/* -maxdepth 0 -type d)"
    IFS=$'\n' read -d '' -ra experiments <<< "$folders"
else
    folders="$(find "$input"  -maxdepth 1 -type d -name "$experiment")"
    IFS=$'\n' read -d '' -ra experiments <<< "$folders"
fi
count=0
for exp in "${experiments[@]}";do
   count=$(( $count + 1 ))
   expOutput="`echo "$exp" | sed "s@$input_dir@@g"`"
   printf "\e[2K  searching: ...$exp{$count/${#experiments[@]}}\r"
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
                folders="$(find "$i"/* -maxdepth 0 -type d | sort -V)"
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
                runOutput=`echo $r | sed "s@$input_dir/$input_base/@@g"`
                if [ $superCondensed = true ];then
                    runOutput=`echo $runOutput | sed "s@experiment@e@g"`
                    runOutput=`echo $runOutput | sed "s@id@i@g"`
                    runOutput=`echo $runOutput | sed "s@Run@r@g"`
                fi
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


                myOutput="$dots$runOutput:   "

                if [ $head = true ];then
                    myHead="`head -n 2 "$r/output/expe-out/out_extra_info.csv" | tail -n 1 `"
                    entries=("$myHead" "${entries[@]}")
                fi
                if [ ${threshold[0]} != false ];then
                    lastEntry=$(( ${#entries[@]} - 1 ))
                    if [[ ${threshold[0]} == "+" ]];then
                        result=$(echo "${entries[$lastEntry]}" | awk -F, -v thresh=${threshold[1]} '{print ($23>thresh) ? 0 : 1}')
                    elif [[ ${threshold[0]} == "-" ]];then
                        result=$(echo "${entries[$lastEntry]}" | awk -F, -v thresh=${threshold[1]} '{print ($23<thresh) ? 0 : 1}')
                    fi
                    if [ $result -eq 1 ];then
                        continue
                    fi
                fi
                if [ $finished = true ];then
                    lastEntry=$(( ${#entries[@]} - 1 ))
                    result=$(echo "${entries[$lastEntry]}" | awk -F, '{print ($21==$20) ? 0 : 1}')
                    if [ $result -eq 1 ];then
                        continue
                    fi
                elif [ $unfinished = true ];then
                    lastEntry=$(( ${#entries[@]} - 1 ))
                    result=$(echo "${entries[$lastEntry]}" | awk -F, '{print ($21 != $20) ? 0 : 1}')
                    if [ $result -eq 1 ];then
                        continue
                    fi
                fi
                printf "\e[2K"
                if [ $setup = true ];then
                    entry="${entries[0]}"
                    setup_output
                    setup=false
                fi
                if [ ${#entries[@]} -gt 1 ] || [ $tryOneliner = false ];then
                        echo "$myOutput"
                fi
                output_tab=`printf "%*s" $(( ${#myOutput} )) " "`
                for entry in "${entries[@]}";do
                        tab=""
                    if [ ${#entries[@]} -gt 1 ] || [ $tryOneliner = false ];then
                        output_tab="\t"
                        tab="\t"
                        myOutput="\t"
                        if [ $condensed = true ];then
                            tab="   "
                            myOutput=""
                        fi
                        if [ $superCondensed = true ];then
                            tab="   "
                            myOutput=""
                        fi
                        format=""
                    fi
                    print_output

                done
            done
        done
    done
done
printf "\e[2K"
echo -e "\nFormat: $endingFormat"
