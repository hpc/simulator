#!/usr/bin/bash

VALID_ARGS=$(getopt -o c:f:do:h --long config:,folder:,download,only:,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi
config="false"
folderloc="false"
download="false"
only="all"
help="false"

eval set -- "$VALID_ARGS"
while true; do
  case "$1" in
    -c | --config)
        config="$2"
        shift 2
        ;;
    -f | --folder)
        folderloc="$2"
        shift 2
        ;;
    -d | --download)
        download="true"
        shift 1
        ;;
    -o | --only)
        only=$2
        shift 2
        ;;
    -h | --help)
        help="true"
        break
        ;;
    --) shift;
        break
        ;;
    esac
done
if [[ $help == "true" ]]
    then
    cat <<EOF
    This script expects you to make a config file that will be used everytime you update.
    Details on its format are at the bottom. It also expects that you are in your batsim_environment

    Usage:
        update_simulator.sh -c <path_to_config> [-f <path_to_folders>|-d] [-o (code|simulator)]

        -c <path>, --config <path>      path to config
        -f <path>, --folder <path>      path to simulator,batsim4,batsched4
        -d, --download                  download latest
        -o ,--only (code|simulator)     only update 'code' or 'simulator', otherwise update all

    config file:
        paths should be absolute expanded paths. input field will not be used with -f or -d options

        input=/path/to/tarfile.tar.gz    include the filename in path
                This tarball should include batsim4, batsched4, and simulator folders
        output=/path/to/simulator         include the simulator folder in path but not a trailing slash '/'
        compileCommand="compile.sh -f <format> -p <path> -m <modules>"

    example:    update_simulator.sh -i /users/<name>/update.config [-o (simulator|code)]


    Script will:
        untar your tarball into temp folder || copy to temp folder || download latest into temp folder
        remove .../simulator/Downloads/[batsim4 and batsched4]
        move the new batsim4 and batsched4 to .../simulator/Downloads/
        move .../simulator/basefiles/batsim_environment.sh  to .../simulator/batsim_environment.sh
        remove .../simulator/basefiles
        move the new simulator/basefiles to .../simulator/
        move .../simulator/batsim_environment.sh to .../simulator/basefiles/
        remove the new simulator folder
        remove the new tarfile
        run compileCommand


EOF
fi
batsim4compile=false
batsched4compile=false


if [[ $only != "all" ]] && [[ $only != "simulator" ]] && [[ $only != "code" ]];then
    echo "Error, -o option only takes 'simulator' or 'code'"
    exit
fi

if [[ $config != "false" ]]
    then
    #source config file
    . $config
    #source batsim_environment
    . "${output}/basefiles/batsim_environment.sh"
    #get the name of the tarball
    file="$(basename $input)"
    #get the folder that the tarball is in and will untar to
    folder="$(dirname $input)"
    #go to this folder
    cd "$folder"
    mkdir -p tmp_update
    if [[ $folderloc != "false" ]]; then
        if [[ $only == "simulator" ]] || [[ $only == "all" ]];then
            cp -R ${folderloc}/simulator ./tmp_update/
        fi
        if [[ $only == "code" ]] || [[ $only == "all" ]];then
            cp -R ${folderloc}/batsim4 ./tmp_update/
            cp -R ${folderloc}/batsched4 ./tmp_update/
        fi
        cd ./tmp_update
    elif [[ $download != "false" ]]; then
        cd ./tmp_update
        if [[ $only == "simulator" ]] || [[ $only == "all" ]];then
            git clone https://github.com/hpc/simulator.git
        fi
        if [[ $only == "code" ]] || [[ $only == "all" ]];then
            git clone https://github.com/hpc/batsim4.git
            git clone https://github.com/hpc/batsched4.git
        fi
    else
        mv $file ./tmp_update
        cd ./tmp_update
        #untar the tarball
        echo "untaring ..."
        tar -xzf $file
    fi
    batsim4compile=false;batsched4compile=false;
    if [[ $only == "code" ]] || [[ $only == "all" ]];then
        #remove the batsim4 and batsched4 folders
        if [ -d batsim4 ];then
            echo "removing old batsim4 code ..."
            rm -rf "${output}/Downloads/batsim4"
            echo "moving new batsim4 code ..."
            mv ./batsim4 "${output}/Downloads/"
            batsim4compile=true
        fi
        if [ -d batsched4 ];then
            echo "removing old batsched4 code ..."
            rm -rf "${output}/Downloads/batsched4"
            echo "moving new batsched4 code ..."
            mv ./batsched4 "${output}/Downloads/"
            batsched4compile=true
        fi
    fi
    if [[ $only == "simulator" ]] || [[ $only == "all" ]];then
        #move the original batsim_environment.sh
        if [ -d simulator ];then
            mv "${output}/basefiles/batsim_environment.sh" "${output}/"
            #remove basefiles and moving new basefiles
            echo "removing old basefiles ..."
            rm -rf "${output}/basefiles" && not_finish=false
            echo "move new basefiles ..."
            mv ./simulator/basefiles "${output}/basefiles"
            #remove the new batsim_environment.sh
            rm -rf "${output}/basefiles/batsim_environment.sh"
            #move the original batsim_environment.sh into basefiles
            mv "${output}/batsim_environment.sh" "${output}/basefiles/"
            #remove new simulator folder
            rm -rf ./simulator
            #remove the tar file
        fi
    fi
    rm $file
    if [[ $only == "code" ]] || [[ $only == "all" ]];then
        #compile both batsim4 and batsched4

        sleep 5
        if [ $batsim4compile = true ];then
            echo "compiling new batsim code ..."
            $compileCommand -o batsim
        fi
        sleep 5
        if [ $batsched4compile = true ];then
            echo "compiling new batsched code ..."
            $compileCommand -o batsched
        fi
    fi
    #print out success message
    echo "***********************************"
    echo ""
    echo "      Successfully updated !!!"
    echo ""
    echo "***********************************"

fi

