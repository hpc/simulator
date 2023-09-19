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

# batFile can be invoked after sourcing this file
# it will help you choose a config file in your $prefix/configs and set it to file1
# as well as help with setting folder1

batFile()
{   
    if [[ $1 == "-h" ]];then
        cat <<"EOF"
                batFile             batFile can be invoked after sourcing this file
                                    It will help you choose a config file in your $prefix/configs and set it to file1
                                    It will also help with setting folder1
        Usage:
            batFile [ls options]

            -[ls options]           Normally 'ls' is invoked to read your $prefix/configs folder without any options.
                                    You may find it helpful to use options to 'ls' such as: sort by time, reverse etc...
                                    Just pass the ls options you normally want to use to batFile and you should be fine.
                                    I suggest using batFile like so:
                                    batFile -ltr
EOF
    
    else

        ls $@ "$prefix/configs" | nl
        files="`ls $@ "$prefix/configs" | nl`"
        IFS=$'\n' read -d '' -ra filesArray <<< "$files"
        printf "\\033[48;5;23;38;5;16;1mEnter a choice:\\033[0m "
        read choice
        choice=`echo $choice | awk '{num=$1-1;print num}'`
        file1="${filesArray[$choice]}"
        file1="`echo "$file1" | awk '{print $NF}'`"
        printf "\\033[48;5;23;38;5;16;1mEnter your folder1 name:\\033[0m \n"
        read -er -i "${file1%.config}" -p "folder1 = "
        folder1=$REPLY
        echo "file1   = $file1"
        printf "\\033[48;5;23;38;5;16;1mNow complete your myBatchTasks command\\033[0m\n"
        bind '"\e[0n":"myBatchTasks.sh -f ${file1} -o ${folder1} "';printf "\e[5n"
    fi

}
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

