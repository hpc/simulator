function updir_complete()
{
    OLD_IFS=$IFS
    tmp_cur=$(dirname `pwd`)
    IFS='/'
    read -ra tmp_dirs <<<"$tmp_cur"
    IFS=$OLD_IFS
    tmp_cur=`pwd`
    if [[ $tmp_cur == '/' ]];then
        tmp_amount=0
    else
        tmp_amount=${#tmp_dirs[@]}
    fi
    if [[ ${COMP_WORDS[1]} == "-r" ]];then
       COMP_WORDS=("${COMP_WORDS[@]:1}")
    fi
    if [[ ${COMP_WORDS[1]} == "-s" ]];then
        tmp_search=($(compgen -W "${tmp_dirs[*]}" "${COMP_WORDS[2]}"))
        if [[ ${#COMP_WORDS[@]} -eq 4 ]];then
            if  [[ ${#tmp_search[@]} -eq 0 ]];then
                return
            else
                COMPREPLY=($(seq 1 1 ${#tmp_search[@]}))
            fi
        elif [[ ${#COMP_WORDS[@]} -eq 3 ]];then
            COMPREPLY=(${tmp_search[@]})
        else
            return
        fi
    else
        tmp_search=($(compgen -W "${tmp_dirs[*]}" "${COMP_WORDS[1]}"))
        if [[ ${#COMP_WORDS[@]} -eq 3 ]];then
            if  [[ ${#tmp_search[@]} -eq 0 ]];then
                return
            else
                COMPREPLY=($(seq 1 1 ${#tmp_search[@]}))
            fi
        elif [[ ${#COMP_WORDS[@]} -eq 2 ]];then
            if [[ $tmp_amount -eq 1 ]] ;then
                if [[ ${COMP_WORDS[1]} == "" ]] ; then
                    COMPREPLY=("1")
                fi
                COMPREPLY+=(${tmp_search[@]})
            elif [[ $tmp_amount -gt 1 ]];then
                if [[ ${COMP_WORDS[1]} == "" ]];then
                    COMPREPLY=("1-$tmp_amount")
                fi
            fi
            COMPREPLY+=(${tmp_search[@]})
        else
            return
        fi
    fi
}


function updir()
{
    if [[ $1 == "" ]] || [[ $1 == "-h" ]]
    then
        cat <<EOF
    updir - go up parent directories
usage:
    updir [-r] <#>                will go up # directories
    updir [-r] <search>           will go up till it finds <search>, can be just the beginning of the directory name
    updir [-r] <search> <#>       same as 'updir <search>' except if there are directories further up the chain that match will choose <#> of matches further up
    updir [-r] -s <search>        the -s flag will force search to be a search term, even if it is a number (directories can be named by a number after all)
    updir [-r] -s <search> <#>
    -r option                     will print the folder and not change directory to it
    updir -h                      display this usage
    updir -e                      display examples

    tab-completion works with this command

-*NOTICE*-  clears the following environment variables: tmp_re, tmp_amount, tmp_search, tmp_cur, tmp_dirs, OLD_IFS     usually no problem at all

EOF
        return 0
    fi
    if [[ $1 == "-e" ]]
    then
        cat <<EOF
example:
             cd /home/craig/dir/dir/spec/6/7/7/7/special/5/4/3/2/1
             updir 1
             pwd        output: /home/craig/dir/dir/spec/6/7/7/7/special/5/4/3/2
             updir 2
             pwd        output: /home/craig/dir/dir/spec/6/7/7/7/special/5/4
             updir spec
             pwd        output: /home/craig/dir/dir/spec/6/7/7/7/special
             updir -s 7
             pwd        output: /home/craig/dir/dir/spec/6/7/7/7
             updir -s 7 2
             pwd        output: /home/craig/dir/dir/spec/6/7/
             updir dir 2
             pwd        output: /home/craig/dir
EOF
        return 0
    fi
    onlyPrint=false
    tmp_cur=`pwd`
    if [[ $1 ==  "-r" ]];
    then
        shift 1
        onlyPrint=true
    fi
    tmp_re='^[0-9]+$'
    if [[ $1 =~ $tmp_re ]]
    then
        tmp_cur=`pwd`
        for i in `seq 1 1 $1`
            do
            if [ $onlyPrint = true ];then
                tmp_cur=`dirname $tmp_cur`
            else
                cd ../
            fi
        done
        if [ $onlyPrint = true ]; then
            echo "$tmp_cur"
        fi
    else
        if [[ $1 == "-s" ]]
        then
            tmp_amount=$3
            tmp_search=$2
        else
            tmp_amount=$2
            tmp_search=$1
        fi
        if ! [[ $tmp_amount =~ $tmp_re ]]
        then
            tmp_amount=1
        fi
        for i in `seq 1 1 $tmp_amount`
        do
            tmp_cur=`echo $tmp_cur | sed -E "s/(.*[/]$tmp_search[^/]*)[/].*/\1/g"`
        done
        if [ $onlyPrint = true ]
        then
            echo $tmp_cur
        else
            cd $tmp_cur
        fi
        
    fi
    unset tmp_amount
    unset tmp_search
    unset tmp_re
    unset tmp_cur
}

complete -F updir_complete updir
