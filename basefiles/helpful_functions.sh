BATVERSION="1.0.5"
#when sourced you will see a '(batsim_env)' in your command prompt
#you will still have your python_env but it won't show '(python_env)'
if [[ $BATSIM_ENV_ACTIVATED == "" ]];then
    BATSIM_ENV_ACTIVATED="TRUE"
    PS1=$(echo $PS1 | sed 's@(python_env)@@g' )
    PS1="(batsim_env)$PS1 "
fi
#to deactivate batsim_env 
#( which is just getting rid of the '(batsim_env)'# and deactivating the python_env)
#use batExit
function batExit
{
    BATSIM_ENV_ACTIVATED=""
    deactivate
    export PS1=$(echo "$PS1" | sed 's@(batsim_env)@@g' )
    tmp=`echo "$PATH" | sed "s@:$prefix/charliecloud/charliecloud/bin:$basefiles_prefix:$install_prefix/bin:/usr/bin:/usr/sbin@@g"`
    export PATH="$tmp"
    tmp=`echo "$LD_LIBRARY_PATH" | sed "s@:$install_prefix/lib:$install_prefix/lib64@@g"`
    export LD_LIBRARY_PATH="$tmp"
}
function batEnv
{
    echo $prefix
}
function batVersion
{
    echo $BATVERSION
}

#helpful bindings I find useful
#just run "bind_all"
function bind_all
{
bind '"\eu":previous-history'
bind '"\em":next-history'
bind '"\ey":history-search-backward'
bind '"\en":history-search-forward'
bind '"\ej":backward-char'
bind '"\ek":forward-char'
bind '"\eh":unix-line-discard'
bind '"\el":beginning-of-line'
bind '"\e;":end-of-line'
bind '"\ep":yank'
bind '"\eg":kill-line'
}
# batFile can be invoked after sourcing this file
# it will help you choose a config file in your $prefix/configs and set it to file1
# as well as help with setting folder1
function batFile
{   
    if [[ $1 == "-h" ]] || [[ $1 == "--help" ]];then
        cat <<"EOF"
        batFile                     batFile can be invoked after sourcing $prefix/basefiles/batsim_environment.sh
                                    It will help you choose a config file in your $prefix/configs and set it to file1
                                    It will also help with setting folder1
        Usage:
            batFile [ls options]

            -[ls options]           Normally 'ls' is invoked to read your $prefix/configs folder without any options.
                                    You may find it helpful to use options to 'ls' such as: sort by time, reverse etc...
                                    Just pass the ls options you would normally want to use to batFile and you should be fine.
                                    I suggest using batFile like so:
                                    batFile -ltr
            ------------------------------------------------------------------------------------------------------------------
            post-running            After running this script you will see the last myBatchTasks command you entered
                                    It checks your ~/.bash_history file for this.  If all that shows up is:
                                    "myBatchTasks -f ${file1} -o ${folder1} "
                                    Then you may need to flush your history with "history -w"
                                    I leave this to the user as you may not want this flushed
EOF
    
    else

        /usr/bin/ls $@ "$prefix/configs" | nl
        files="`/usr/bin/ls $@ "$prefix/configs" | nl`"
        IFS=$'\n' read -d '' -ra filesArray <<< "$files"
        printf "\\033[48;5;23;38;5;16;1mEnter a choice (0 to exit):\\033[0m "
        read choice
        choice=`echo $choice | awk '{num=$1-1;print num}'`
        if [[ $choice == -1 ]];then
            return
        fi
        file1="${filesArray[$choice]}"
        file1="`echo "$file1" | awk '{print $NF}'`"
        printf "\\033[48;5;23;38;5;16;1mEnter your folder1 name:\\033[0m \n"
        read -er -i "${file1%.config}" -p "folder1 = "
        folder1=$REPLY
        echo "file1   = $file1"
        printf "\\033[48;5;23;38;5;16;1mNow complete your myBatchTasks command\\033[0m\n"
        last=$(grep '^myBatchTasks.sh -f ${file1} -o ${folder1} ' ~/.bash_history | tail -n 1)
        if [[ $last == "" ]];then
            last='myBatchTasks.sh -f ${file1} -o ${folder1} '
        fi
        bind "\"\e[0n\":\"$last\"";printf "\e[5n"
    fi

}
function batFolder_complete
{
  if [[ ${COMP_WORDS[${#COMP_WORDS[@]}-2]} == "-d" ]] || [[ ${COMP_WORDS[${#COMP_WORDS[@]}-1]} ]];then
    tmp_dirs=()
    for i in ~/.DirB/*; do
        tmp_dirs+=($(basename "$i"))
    done
    COMPREPLY=()
    tmp_search=($(compgen -W "${tmp_dirs[*]}" "${COMP_WORDS[${#COMP_WORDS[@]}-1]}"))
    if [[ ${#tmp_search[@]} -eq 0 ]]; then
        return
    else
        COMPREPLY+=( ${tmp_search[@]})
    fi
  fi

}
function batFolder
{
    if [[ $1 == "-h" ]] || [[ $1 == "--help" ]];then
        cat <<"EOF"
        batFile                     batFolder can be invoked after sourcing $prefix/basefiles/batsim_environment.sh
                                    It will help you choose a folder in your $prefix/experiments and set it to folder1
        Usage:
            batFolder [-#] [-i <path | -d <bookmark>] [ls options]

            -#                      Normally sets the chosen folder to folder1 but you can choose folder1-folder9 with -1,-2,...,-9 flag

            -i <path>               Normally $prefix/experiments is used, but if you have another folder to use set it here.

            -d <bookmark>           If using dirB  will use the bookmark specified as the folder

            -[ls options]           Normally 'ls' is invoked to read your $prefix/experiments folder without any options.
                                    You may find it helpful to use options to 'ls' such as: sort by time, reverse etc...
                                    Just pass the ls options you would normally want to use to batFile and you should be fine.
                                    I suggest using batFile like so:
                                    batFile -ltr
            ------------------------------------------------------------------------------------------------------------------
            post-running            After running this script you will see the last myBatchTasks command you entered
                                    It checks your ~/.bash_history file for this.  If all that shows up is:
                                    "myBatchTasks -f ${file1} -o ${folder1} "
                                    Then you may need to flush your history with "history -w"
                                    I leave this to the user as you may not want this flushed
EOF

    else
        num=0
        myRegEx="[-][1-9]"
        if [[ $1 =~ $myRegEx ]];then
            num=${1:1}
            options=${@:2}
        fi
        echo $options
        echo $num
        if [[ $1 == "-i" ]];then
            input="${2%/}"
            options=${@:3}
        elif [[ $1 == "-d" ]];then
            input="$(d $2)"
            options=${@:3}
        elif [[ $2 == "-i" ]];then
            input="${3%/}"
            options=${@:4}
        elif [[ $2 == "-d" ]];then
            input="$(d $3)"
            options=${@:4}
        else
            input="$prefix/experiments"
            if [ $num -eq 0 ];then
                options=$@
            fi
        fi
        if [ $num -eq 0 ]; then
            num=1
        fi
        enter=false
        /usr/bin/ls ${options} -d "$input"/*/ | sed "s#[/].*[/]\(.*\)/#\1#g" | nl
        folders="`/usr/bin/ls ${options} -d "$input"/*/ | sed "s#[/].*[/]\(.*\)/#\1#g" | nl`"
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
            return
        fi

        input_dir="${input}"
        input_base="${foldersArray[$choice]}"
        input_base="`echo "$input_base" | awk '{print $NF}'`"
        #printf -v "folder${num}" '%s' "$input_dir/$input_base"
        eval export "folder${num}"="$input_dir/$input_base"
        if [ $enter = true ];then
            batFolder -$num -i "$input_dir/$input_base"
            
        fi
    fi
}

complete -F batFolder_complete batFolder
complete -F batFolder_complete progress.sh 
