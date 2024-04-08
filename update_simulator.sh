#!/usr/bin/bash
if [[ $1 == "-h" ]] || [[ $1 == "--help" ]]
    then
    echo <<EOF
    This script expects you to make a config file that will be used everytime you update.
    Details on its format are at the bottom. It also expects that you are in your batsim_environment
    
    Usage:
        update_simulator.sh -i <path_to_config>
        
    config file:

        input=/path/to/tarfile.tar.gz    include the filename in path
                This tarball should include batsim4, batsched4, and simulator folders
        output=/path/to/simulator         include the simulator folder in path but not a trailing slash '/'
        compileCommand="compile.sh -f <format> -p <path> -m <modules>"

    example:    update_simulator.sh -i /users/<name>/update.config


    Script will:
        untar your tarball
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

if [[ $1 == "-i" ]]
    then
    #source config file
    . "$2"
    #source batsim_environment
    . "${output}/basefiles/batsim_environment.sh"
    #get the name of the tarball
    file="$(basename $input)"
    #get the folder that the tarball is in and will untar to
    folder="$(dirname $input)"
    #go to this folder
    cd "$folder"
    #untar the tarball
    echo "untaring ..."
    tar -xf $file
    #remove the batsim4 and batsched4 folders
    echo "removing old code ..."
    rm -rf "${output}/Downloads/batsim4"
    rm -rf "${output}/Downloads/batsched4"
    #move the new batsim4 and batsched4 folders
    echo "move new code ..."
    mv ./batsim4 "${output}/Downloads/"
    mv ./batsched4 "${output}/Downloads/"
    #move the original batsim_environment.sh
    mv "${output}/basefiles/batsim_environment.sh" "${output}/"
    #remove basefiles and moving new basefiles
    echo "removing old basefiles ..."
    rm -rf "${output}/basefiles" && not_finish=false
    echo "move new basefiles ..."
    mv ./simulator/basefiles "${output}/"
    #remove the new batsim_environment.sh
    rm -rf "${output}/basefiles/batsim_environment.sh"
    #move the original batsim_environment.sh into basefiles
    mv "${output}/batsim_environment.sh" "${output}/basefiles/"
    #remove new simulator folder
    rm -rf ./simulator
    #remove the tar file
    rm $file
    #compile both batsim4 and batsched4
    echo "compiling new code ..."
    sleep 5
    $compileCommand
    #print out success message
    echo "***********************************"
    echo ""
    echo "      Successfully updated !!!"
    echo ""
    echo "***********************************"

fi