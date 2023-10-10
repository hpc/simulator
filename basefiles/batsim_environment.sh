#############################################################################
# Edit prefix before doing anything, this is mandatory
#
# Here you will find some SBATCH variables you can set
# All SBATCH variables can be set here, not just the ones
# included.  And of course uncomment the line to take effect.
# ALL SBATCH variables can be found here:
# https://slurm.schedmd.com/sbatch.html#SECTION_INPUT-ENVIRONMENT-VARIABLES
#
# This file can be edited after ./myBatchTasks.sh
# finishes for another batch of simulations with different
# parameters.  Just make sure you keep up with socket-start
# so no sims are overlapping with socket numbers
#############################################################################




#export prefix=?

#export SBATCH_PARTITION=standard
#export SBATCH_QOS=standard
#export SBATCH_NO_REQUEUE="yes"

export basefiles_prefix=$prefix/basefiles
export install_prefix=$prefix/Install
export downloads_prefix=$prefix/Downloads
export python_prefix=$prefix/python_env

export PATH=$PATH:$prefix/charliecloud/charliecloud/bin:$basefiles_prefix:$install_prefix/bin:/usr/bin:/usr/sbin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$install_prefix/lib:$install_prefix/lib64
export LMOD_SH_DBG_ON=1
source $python_prefix/bin/activate


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
batExit()
{
    BATSIM_ENV_ACTIVATED=""
    deactivate
    export PS1=$(echo "$PS1" | sed 's@(batsim_env)@@g' )
    tmp=`echo "$PATH" | sed "s@:$prefix/charliecloud/charliecloud/bin:$basefiles_prefix:$install_prefix/bin:/usr/bin:/usr/sbin@@g"`
    export PATH="$tmp"
    tmp=`echo "$LD_LIBRARY_PATH" | sed "s@:$install_prefix/lib:$install_prefix/lib64@@g"`
    export LD_LIBRARY_PATH="$tmp"
}
batEnv()
{
    echo $prefix
}

#helpful bindings I find useful
#just run "bind_all"
bind_all()
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
batFile()
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

        ls $@ "$prefix/configs" | nl
        files="`ls $@ "$prefix/configs" | nl`"
        IFS=$'\n' read -d '' -ra filesArray <<< "$files"
        printf "\\033[48;5;23;38;5;16;1mEnter a choice:\\033[0m "
        read choice
        choice=`echo $choice | awk '{num=$1-1;print num}'`
        if [[ $choice == 0 ]];then
            exit
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

