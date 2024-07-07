#!/usr/bin/bash
GPP_MAJ=5
CMAKE_MAJ=3
CMAKE_MIN=11
printUsage()
{
cat <<"EOF"


    deploy.sh               automates the downloading compiling and building of batsim into different formats and in different conditions.
                            NOTE: For charliecloud and bare-metal, gcc,make,cmake,python3 etc... is assumed to be working and a recent version.

Usage:
  [1]  deploy.sh -f <STR>  [-x][-l]  [--no-internet ( [-p] | [-u] | [-c] )] [--with-gui]
  [2]  deploy.sh --gui -f <STR> [--no-internet ([-p] | [-u]) ]
  [3]  deploy.sh --convert-charliecloud <PATH> -o <PATH> [-m <STR>] [-l <INT>]
  [4]  deploy.sh --clean

Required Options 1:

    -f, --format <STR>              The format to build things for:
                                    bare-metal | charliecloud | docker

Optional Options 1:
    -x, --prefix  <STR>             Only used with --format=bare-metal.
                                    The full path to the folder that everything is going to install to
                                    Typically the /path/to/simulator folder.

    -l, --line-number <INT>         Only used with --format=bare-metal.
                                    The line number into deploy_commands to start at.

    -n, --no-internet               Only used with --format=charliecloud || bare-metal
                                    '   When using bare-metal, will require gcc/cmake and build-tools on remote computer.
                                    '   Will also require time on the remote computer, as everything will need to compile.  About an hour.
                                    If set, will package a folder up that you can then move to
                                    the computer with no internet.  The folder is about a 3.5GB
                                    folder with tar.gz files inside.
                                    Must use -p or -u or -c options with this.

    -m, --modules <STR>             Load modules in comma seperated STR.  Used only with --format bare-metal
                                    ' example: --modules "gcc/10.3.0,cmake/3.22.3"

    -p, --package                   Only used with --no-internet.
                                    Will initiate the packaging of batsim

    -u, --un-package                Only used with --no-internet.
                                    Will initiate the un-packaging of batsim.
                                    ' when --format=bare-metal, will initiate the compiling of all necessary code as well

    -c, --continue-unpacking        Will continue the un-packaging of batsim with --line-number.  Only used with
                                    --format=bare-metal and --no-internet

    --with-gui                      TODO When this flag is given, gui components will be installed as well.
                                    Gui components are text/terminal based

Required Options 2:
    --gui                           TODO only deploy the gui.
                                    Meant to be run after normal deployment if you later decide you want the gui.
                                    Uses install_prefix environment variable from sourcing .../basefiles/batsim_environment.sh

    -f, --format <STR>              The format to build things for:
                                    bare-metal | charliecloud | docker

    -n, --no-internet               Only used with --format=charliecloud
                                    If set, will package a folder up that you can then move to
                                    the computer with no internet.
                                    Must use -p or -u options with this.
Required Options 3:
    --convert-charliecloud          Convert charliecloud deployment to bare-metal
                                    Provide the full path to the charliecloud (batsim_ch folder)
                                    ' example: --convert-charliecloud /path/to/simulator/batsim_ch

    -o, --output                    Where to put Install folder
                                    ' example: --convert-charliecloud /path/to/simulator/batsim_ch -o /path/to/simulator
                                    ' creates /path/to/simulator/Install with all your needed programs compiled in
                                    ' /path/to/simulator/Install/bin
Optional Options 3:
    -m, --modules <STR>             Load modules in comma seperated STR
                                    ' example: --modules "gcc/10.3.0,cmake/3.22.3"

    -l, --line-number <INT>         The line number into deploy_commands_no_internet to start at

Required Options 4:

    --clean                         Will clean up the basefiles folder from a previous deploy



    -h, --help                      Display this usage page

EOF
    exit 1
}
VALID_ARGS=$(getopt -o f:npux:l:ho:m:c --long clean,format:,no-internet,continue-unpacking,package,un-package,prefix:,line-number:,with-gui,gui,convert-charliecloud:,modules:,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi
MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
MY_PATH="$(cd -- "$MY_PATH" && pwd)"
default_prefix="$(cd -- "$MY_PATH/.." && pwd)"
if [[ $prefix == "" ]];then
    prefix=false
fi

OUTPUT=false
CONVERT=false
FORMAT=false
NO=false
PACK=false
UNPACK=false
PREFIX=false
LINE=false
HELP=false
CLEAN=false
modules=false
gui=false
withGui=false
count=0
CONTINUE=false
eval set -- "$VALID_ARGS"
while true; do
  case "$1" in
    --clean)
        CLEAN=true
        shift 1
        ;;
    -f | --format)
        FORMAT="$2"
        count=$(( $count + 1 ))
        shift 2
        ;;
    -o | --output)
        OUTPUT="$2"
        count=$(( $count + 1 ))
        shift 2
        ;;
    --convert-charliecloud)
        CONVERT="$2"
        count=$(( $count + 1 ))
        shift 2
        ;;
    -m | --modules)
        modules="$2"
        count=$(( $count + 1 ))
        shift 2
        ;;
    -c | --continue-unpacking)
        CONTINUE=true
        UNPACK=true
        count=$(( $count + 1 ))
        shift 1
        ;;
    --with-gui)
        withGui=true
        count=$(( $count + 1 ))
        shift 1
        ;;
    --gui)
        gui=true
        count=$(( $count + 1 ))
        shift 1
        ;;
    -x | --prefix)
        PREFIX="$2"
        count=$(( $count + 1 ))
        shift 2
        ;;
    -l | --line-number)
        LINE="$2"
        count=$(( $count + 1 ))
        shift 2
        ;;
    -n | --no-internet)
        NO=true
        count=$(( $count + 1 ))
        shift 1
        ;;
    -p | --package)
        PACK=true
        count=$(( $count + 1 ))
        shift 1
        ;;
    -u | --un-package)
        UNPACK=true
        count=$(( $count + 1 ))
        shift 1
        ;;
    -h | --help)
        HELP=true
        break
        ;;
    --) shift;
        break
        ;;
  esac
done
# if help or no format
# if not bare-metal but prefix or line set
# if format not one of charliecloud | bare-metal | docker
# if format is not charliecloud but any of -nup is used
# if format is charliecloud but -n is not used and -up are used
# if format is charliecloud and -n is used but both -up are used or -n is used but neither -up are used
echo "$FORMAT , $NO, $PACK, $UNPACK"
if [ $CLEAN = false ]; then
if [ $CONVERT = false ]; then
if [ $HELP = true ] || [ $FORMAT = false ];then
    echo "1"
    printUsage
fi
if ([ $FORMAT != 'bare-metal' ] && ( [ $PREFIX != false ] || [ $LINE != false ] ));then
    echo "2"
    printUsage
fi
if ([ $FORMAT != 'charliecloud' ] && [ $FORMAT != 'bare-metal' ] && [ $FORMAT != 'docker' ]);then
    echo "3"
    printUsage
fi
if ( ( [ $FORMAT != 'charliecloud' ] && [ $FORMAT != 'bare-metal' ] ) && ( [ $NO = true ] || [ $PACK = true ] || [ $UNPACK = true ] ) );then
    echo "4"
    printUsage
fi
if ( ([ $FORMAT == 'charliecloud' ] || [ $FORMAT == 'bare-metal' ]) && ([ $NO = false ] && ( [ $PACK = true ] || [ $UNPACK = true ]) ) );then
    echo "5"
    printUsage
fi
if ( ([ $FORMAT == 'charliecloud' ] || [ $FORMAT == 'bare-metal' ]) && [ $NO = true ] && ( ( [ $PACK = true ] && [ $UNPACK = true ] ) || ( [ $PACK = false ] && [ $UNPACK = false ] )));then
    echo "6"
    printUsage
fi

fi
fi

if [ $modules != false ];then
    for i in $(echo $modules | tr "," "\n");do
        module load "$i"
    done
fi

function deployGui
{
    if [[ $FORMAT == "docker" ]];then
        prefix="/home/sim/simulator"
        FORMAT="bare-metal"
    fi
    if [ $prefix = false ];then
        if [ $PREFIX = false ];then
            echo "default: $default_prefix"
            echo "Environment variable 'prefix' is not set and you did not add -x option."
            echo "Enter your desired prefix (0 for default):"
            read prefix
        else
            prefix=$PREFIX
        fi
        if [[ $prefix == "0" ]];then
            prefix=$default_prefix
        fi
    fi
    case $FORMAT in
        "bare-metal")
            which libtool > /dev/null 2>&1
            hasLibtool=$?
            if [[ $hasLibtool == 1 ]];then
                which libtoolize > /dev/null 2>&1
                hasLibtoolize=$?
                if [[ $hasLibtoolize == 1 ]];then
                    echo "you don't have libtool or libtoolize installed.  Possibly check if you have the correct modules loaded. Look at 'module avail' and 'module load'"
                    exit
                else
                    libtoolize_path=`which libtoolize`
                    export ACLOCAL_PATH=${libtool_path%/bin/libtoolize}/share/aclocal
                fi
            else
                libtool_path=`which libtool`
                export ACLOCAL_PATH=${libtool_path%/bin/libtool}/share/aclocal
            fi
            cmakeV=`cmake --version | grep -o -E "[0-9]+[.][0-9.]+"`
            cmakeMaj=`echo $cmakeV | awk -F. '{print $1}'`
            cmakeMin=`echo $cmakeV | awk -F. '{print $2}'`
            if [[ $cmakeMaj < $CMAKE_MAJ ]];then
                echo "ERROR cmake version too low"
                echo "your major version of cmake is '$cmakeMaj'.  It needs to be at least version '$CMAKE_MAJ'. Using version: '$cmakeV'.  You need at least version $CMAKE_MAJ.$CMAKE_MIN"
                echo "Possibly check if you have the correct modules loaded.  Look at 'module avail' and 'module load'"
                exit
            fi
            if [[ $cmakeMin < $CMAKE_MIN ]];then
                echo "ERROR cmake version too low"
                echo "your minor version of cmake is '$cmakeMin'.  It needs to be at least version '$CMAKE_MIN'. Using version: '$cmakeV'.  You need at least version $CMAKE_MAJ.$CMAKE_MIN"
                echo "Possibly check if you have the correct modules loaded.  Look at 'module avail' and 'module load'"
                exit
            fi
            gppV=`g++ --version | grep -o -E "[0-9]+[.][0-9.]+"`
            gppMaj=`echo $gppV | awk -F. '{print $1}'`
            gppMin=`echo $gppV | awk -F. '{print $2}'`
            if [[ $gppMaj < $GPP_MAJ ]];then
                echo "ERROR g++ version too low"
                echo "your major version of g++ is '$gppMaj'.  It needs to be at least version '$GPP_MAJ'. Using version: '$gppV'.  You need at least version $GPP_MAJ"
                echo "Possibly check if you have the correct modules loaded.  Look at 'module avail' and 'module load'"
                exit
            fi
            export basefiles_prefix=$prefix/basefiles
            export install_prefix=$prefix/Install
            export downloads_prefix=$prefix/Downloads
            export python_prefix=$prefix/python_env

            export PATH=$PATH:$basefiles_prefix:$install_prefix/bin:/usr/bin:/usr/sbin
            export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$install_prefix/lib:$install_prefix/lib64
            . $basefiles_prefix/deploy_gui
            gui_build
        ;;
        "charliecloud")
            if [ $NO = false ];then
                ch_bin=$prefix/charliecloud/charliecloud/bin
                ch_loc=$prefix/batsim_ch
                python_prefix=/home/sim/simulator/python_env
                install_prefix=/home/sim/simulator/Install
                $ch_bin/ch-run $ch_loc --write  -- /bin/bash -c 'source /home/sim/.environ; source $basefiles_prefix/deploy_gui;gui_build'
            elif [ $NO = true ] && [ $PACK = true ];then
                mkdir -p $prefix/gui_package/downloads && cd $prefix/gui_package/downloads
                . $prefix/basefiles/deploy_gui
                downloads_prefix=$prefix/gui_package/downloads
                gui_download
                cd $prefix/gui_package
                tar -czf $prefix/gui_package/downloads.tar.gz ./downloads
                rm -rf $prefix/gui_package/downloads
                echo "1. Move 'prefix'/gui_package to remote computer"
                echo "2. On remote computer move gui_package to the 'prefix' there(your simulator folder)"
                echo "3. Run deploy.sh --gui -f charlieclod --no-internet -u"
            elif [ $NO = true ] && [ $UNPACK = true ];then
                ch_bin=$prefix/charliecloud/charliecloud/bin
                ch_loc=$prefix/batsim_ch
                python_prefix=/home/sim/simulator/python_env
                install_prefix=/home/sim/simulator/Install
                cd $prefix/gui_package
                if [ $? -eq 1 ];then
                    echo "$prefix/gui_package not found.  Did you move the gui_package to your simulator folder?"
                    exit 1
                fi
                tar -xf $prefix/gui_package/downloads.tar.gz
                downloads_prefix=/home/sim/simulator/Downloads
                basefiles_prefix=/home/sim/simulator/basefiles
                $ch_bin/ch-run $ch_loc --write --bind "${prefix}/gui_package/downloads":/mnt/FOLDER1 -- /bin/bash -c "source /home/sim/.environ; source $basefiles_prefix/deploy_gui;gui_move;gui_compile_all"
                echo "You are all set.  You can delete 'prefix'/gui_package now if you want"
            fi

                
        ;;
    esac
 exit 0
}
if [ $CLEAN = true ];then
    basefiles=$MY_PATH
    rm -rf $basefiles/CharlieCloud_compile/download $basefiles/CharlieCloud_compile/boost_1_75_0
    rm -rf $basefiles/charliecloud
    rm -rf $basefiles/Docker_compile/download $basefiles/Docker_compile/boost_1_75_0
    rm -f $basefiles/deploy.config
    exit 0
fi
if [ $CONVERT != false ] && [ $OUTPUT != false ];then
    export prefix=$OUTPUT
    export basefiles_prefix=$prefix/basefiles
    export python_prefix=$prefix/python_env
    export downloads_prefix=$CONVERT/home/sim/simulator/Downloads
    export old_install_prefix=$CONVERT/home/sim/simulator/Install
    export install_prefix=$OUTPUT/Install
    export PATH=$PATH:$install_prefix/bin
    export PKG_CONFIG_PATH=$install_prefix/lib/pkgconfig:$install_prefix/lib64/pkgconfig
    export BOOST_ROOT=$install_prefix
    . $python_prefix/bin/activate
    mkdir -p $install_prefix
    end_line=`cat $basefiles_prefix/deploy_commands_no_internet | wc -l`
    oneliner=1
    line_number=1
    if [ $LINE != false ];then
        line_number=$LINE
    fi
    for i in `seq $line_number 1 $end_line`
    do
        if [[ $oneliner -eq 0 ]]
        then
            line=`tr -d '\\' <<< $line`
            current=`sed -n ${i}p $basefiles_prefix/deploy_commands_no_internet`
            line="$line $current"
        else
            line=`sed -n ${i}p $basefiles_prefix/deploy_commands_no_internet`
        fi
        echo "line: $line_number  cmd:$line"
        oneliner=0
        process_line=`grep -E '.*[\]$' <<<$line`
        if [[ $process_line -eq "" ]]
        then
            oneliner=1
        else
            continue
        fi
        OLD_LINE=$line_number
        eval "CFLAGS='-Wno-error' CXXFLAGS='-Wno-error' $line"
        return_value=$?
        if [[ $line_number != $OLD_LINE ]];then
            sleep 5
        fi
        if [[ $line_number != "boost" ]]
        then

            if [[ $return_value -eq 1 ]]
            then

                echo "Error after line_number: $line_number"
                echo "Try to fix error and start this script again. Exiting..."
                echo "$line_number" > $basefiles_prefix/deploy.config
                echo "$prefix" >> $basefiles_prefix/deploy.config
                exit 1
            fi
        fi

            if [[ $line_number == "end" ]]
        then
            cp $old_install_prefix/bin/robin $install_prefix/bin/

            cat <<EOF
            *********************************************

            Successfully Installed Batsim and Batsched!!!

            *********************************************

            You will want to make sure .../basefiles/batsim_environment.sh is edited with options you need
            At a bare minimum set prefix=? to the correct prefix. This is probably going to be the full path to your simulator folder.
EOF
        fi


    done
    if [ $gui = true ];then
        deployGui
    fi
    exit 0
fi
if [ $FORMAT = 'bare-metal' ] && [ $NO = true ] && [ $PACK = true ];then
    basefiles=$MY_PATH
    deactivate
    cd ../
    prefix=${MY_PATH%/basefiles}
    export basefiles_prefix=$prefix/basefiles
    export python_prefix=$prefix/python_env
    export downloads_prefix=$prefix/Downloads
    export install_prefix=$prefix/Install
    mkdir -p $downloads_prefix && \
    mkdir -p $install_prefix/bin/ && \
    mkdir -p $python_prefix && \
    cd $python_prefix
    python3 -m venv ./
    . ./bin/activate
    python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip
    python3 -m pip install meson
    python3 -m pip install ninja
    python3 -m pip install pandas
    python3 -m pip install numpy
    python3 -m pip install seaborn
    python3 -m pip install shapely
    python3 -m pip install requests
    python3 -m pip install venv-pack
    export python3_ver=`python3 --version | awk '{print $2}' | awk -F. '{print $1"."$2}'`
    export file="$python_prefix/lib/python${python3_ver}/site-packages/mesonbuild/backend/backends.py"
    sed -i 's/\(if delta > \)\([0-9]\+[.][0-9]\+\)\(.*\)/\15.0\3/g' $file
    venv-pack -o $prefix/python_env.tar.gz
    cd $downloads_prefix
    wget --no-check-certificate https://sourceforge.net/projects/boost/files/boost/1.75.0/boost_1_75_0.tar.gz/download
    tar -xf ./download
    cd $downloads_prefix
    git clone https://deploy-1:x8BEfHUytzmT78ftoTnY@gitlab.newmexicoconsortium.org/lanl-ccu/batsim4.git
    git clone https://deploy-1:_CmeAypLDgszp8SANVsm@gitlab.newmexicoconsortium.org/lanl-ccu/batsched4.git
    cd $basefiles_prefix
    git clone https://cswalke1:ekhr1Q_mL356zvCt_p2B@gitlab.newmexicoconsortium.org/lanl-ccu/simulator.git
    cd $downloads_prefix
    git clone https://framagit.org/simgrid/simgrid.git
    git clone https://github.com/zeromq/libzmq.git
    git clone https://github.com/redis/hiredis.git
    git clone https://github.com/enki/libev.git
    git clone https://github.com/alisw/GMP.git
    git clone https://github.com/zeromq/cppzmq.git
    git clone https://github.com/mpoquet/redox.git
    git clone https://github.com/Tencent/rapidjson.git
    git clone https://github.com/zeux/pugixml.git
    git clone https://github.com/google/googletest.git
    git clone https://framagit.org/batsim/intervalset.git
    git clone https://github.com/docopt/docopt.cpp.git
    git clone https://github.com/emilk/loguru.git
    export GO111MODULE=on
    export GOBIN=$install_prefix/bin
    export GOROOT=$downloads_prefix/go
    cd $downloads_prefix
    wget --no-check-certificate https://go.dev/dl/go1.19.2.linux-amd64.tar.gz
    tar -xf go1.19.2.linux-amd64.tar.gz
    mv ./go/bin/go $install_prefix/bin/
    $install_prefix/bin/go install -v framagit.org/batsim/batexpe/cmd/robin@latest
    $install_prefix/bin/go install -v framagit.org/batsim/batexpe/cmd/robintest@latest
    
    cd $prefix
    mkdir experiments
    mkdir configs
    rm -rf $prefix/python_env
    cd $prefix/..
    cp $basefiles/deploy.sh ./
    tar -czf batsim.tar.gz ./$(basename $prefix)
    mkdir -p batsim_packaged
    mv batsim.tar.gz ./batsim_packaged/
    mv deploy.sh ./batsim_packaged/
    echo $(basename $prefix) > ./batsim_packaged/prefixName.txt
    cat <<EOF
        ******************************************************************************************************************************************
        Finished making your packaged directory
    
        1. copy $(dirname $prefix)/batsim_packaged folder over to computer with no internet
        2. then run this same script with un-package argument and look at modules argument as well
        3. If any errors happen during un-package you can use the -c and -l arguments after correcting the errors

        *******************************************************************************************************************************************
EOF
    exit 0
fi
if [ $FORMAT = 'bare-metal' ] && [ $NO = true ] && [ $UNPACK = true ] && [ $CONTINUE = false ];then
    pack_prefix=$MY_PATH
    prefixName=`cat $pack_prefix/prefixName.txt`
    tar -xf batsim.tar.gz
    export prefix=$pack_prefix/$prefixName
    cd $prefix
    mkdir python_env
    mv python_env.tar.gz $prefix/python_env
    cd $prefix/python_env
    tar -xf python_env.tar.gz
    if [ -d ./python_env ];then
        mv ./python_env $prefix/python_tmp
        rm -rf $prefix/python_env
        mv $prefix/python_tmp $prefix/python_env
    fi
    cd $prefix
    export basefiles_prefix=$prefix/basefiles
    export python_prefix=$prefix/python_env
    export downloads_prefix=$prefix/Downloads
    export install_prefix=$prefix/Install
    export PATH=$PATH:$install_prefix/bin
    export PKG_CONFIG_PATH=$install_prefix/lib/pkgconfig:$install_prefix/lib64/pkgconfig
    export BOOST_ROOT=$install_prefix
    export MY_PATH=$basefiles_prefix
    cat <<EOF
            *********************************************

            Successfully Unpacked Batsim !!!
            Getting Ready To Compile Dependencies of Batsim and Batsim itself......

            *********************************************
EOF
    sleep 10
    rm $pack_prefix/deploy.sh
    cat <<EOF
            ***************************************************************************
                Deleted .../batsim_packaged/deploy.sh

                Future invocations of deploy.sh should
                come from .../batsim_packaged/simulator/basefiles/deploy.sh
                
                If errors happen during unpacking you can now use -c and -l arguments
                to start where you left off

            ****************************************************************************
EOF
    sleep 10
fi
if [ $FORMAT = 'bare-metal' ] && [ $NO = true ] && [ $UNPACK = true ];then
    export prefix=${MY_PATH%/basefiles}
    export basefiles_prefix=$prefix/basefiles
    export python_prefix=$prefix/python_env
    export downloads_prefix=$prefix/Downloads
    export install_prefix=$prefix/Install
    export PATH=$PATH:$install_prefix/bin
    export PKG_CONFIG_PATH=$install_prefix/lib/pkgconfig:$install_prefix/lib64/pkgconfig
    export BOOST_ROOT=$install_prefix
   

    . $python_prefix/bin/activate
    end_line=`cat $basefiles_prefix/deploy_commands_no_internet_checkout | wc -l`
    oneliner=1
    line_number=1
    if [ $LINE != false ];then
        line_number=$LINE
    fi
    for i in `seq $line_number 1 $end_line`
    do
        if [[ $oneliner -eq 0 ]]
        then
            line=`tr -d '\\' <<< $line`
            current=`sed -n ${i}p $basefiles_prefix/deploy_commands_no_internet_checkout`
            line="$line $current"
        else
            line=`sed -n ${i}p $basefiles_prefix/deploy_commands_no_internet_checkout`
        fi
        echo "line: $line_number  cmd:$line"
        oneliner=0
        process_line=`grep -E '.*[\]$' <<<$line`
        if [[ $process_line -eq "" ]]
        then
            oneliner=1
        else
            continue
        fi
        OLD_LINE=$line_number
        eval "CFLAGS='-Wno-error' CXXFLAGS='-Wno-error' $line"
        return_value=$?
        if [[ $line_number != $OLD_LINE ]];then
            sleep 5
        fi
        if [[ $line_number != "boost" ]]
        then

            if [[ $return_value -eq 1 ]]
            then

                echo "Error after line_number: $line_number"
                echo "Try to fix error and start this script again. Exiting..."
                echo "$line_number" > $basefiles_prefix/deploy.config
                echo "$prefix" >> $basefiles_prefix/deploy.config
                exit 1
            fi
        fi

            if [[ $line_number == "end" ]]
        then

            cat <<EOF
            *****************************************************************

            Successfully Compiled and Installed Batsim and Batsched!!!

            *****************************************************************


            ***********************************************************************************************************************************
            *    You will want to make sure .../basefiles/batsim_environment.sh is edited with options you need                               *
            *    At a bare minimum set prefix=? to the correct prefix. This is probably going to be the full path to your simulator folder.   *
            ***********************************************************************************************************************************
EOF
        fi
    done


exit 0
fi

if [ $FORMAT = 'bare-metal' ] && [ $NO = false ];then

    myDir=$MY_PATH
    echo "myDir=$myDir"
    touch $myDir/deploy.config
    line_number=`sed -n 1p $myDir/deploy.config`
    end_line=`cat $myDir/deploy_commands | wc -l`
    if [ $LINE = false ]
    then
        if [ $PREFIX = false ]
        then
        echo "default: $default_prefix"
        echo "Enter the absolute folder you want to download and install things to (0 for default):"
        read prefix
        else
        prefix=$PREFIX
        fi
        if [[ $prefix == "0" ]];then
            prefix="$default_prefix"
        fi
        mkdir -p $prefix
        line_number=1
        echo $line_number > $myDir/deploy.config
        echo "$prefix" >> $myDir/deploy.config
    fi
    if [ $LINE != false ]
    then
    line_number=$LINE
        if [ $PREFIX = false ]
            then
            echo "default: $default_prefix"
            echo "Enter the absolute folder you want to download and install things to (0 for default):"
            read prefix
            else
            prefix=$PREFIX
        fi
        if [[ $prefix == "0" ]];then
            prefix="$default_prefix"
        fi
        mkdir -p $prefix
        echo $line_number > $myDir/deploy.config
        echo "$prefix" >> $myDir/deploy.config
    fi
    . genPrefix
    mkdir -p $downloads_prefix && \
    mkdir -p $install_prefix && \
    mkdir -p $python_prefix && \
    oneliner=1
    for i in `seq $line_number 1 $end_line`
    do
        if [[ $oneliner -eq 0 ]]
        then
            line=`tr -d '\\' <<< $line`
            current=`sed -n ${i}p $basefiles_prefix/deploy_commands`
            line="$line $current"
        else
            line=`sed -n ${i}p $basefiles_prefix/deploy_commands`
        fi
        echo "line: $line_number  cmd:$line"
        oneliner=0
        process_line=`grep -E '.*[\]$' <<<$line`
        if [[ $process_line -eq "" ]]
        then
            oneliner=1
        else
            continue
        fi
        OLD_LINE=$line_number
        eval "CFLAGS='-Wno-error' CXXFLAGS='-Wno-error' $line"
        return_value=$?
        if [[ $line_number != $OLD_LINE ]];then
            sleep 5
        fi
        if [[ $line_number != "boost" ]]
        then

            if [[ $return_value -eq 1 ]]
            then

                echo "Error after line_number: $line_number"
                echo "Try to fix error and start this script again. Exiting..."
                echo "$line_number" > $basefiles_prefix/deploy.config
                echo "$prefix" >> $basefiles_prefix/deploy.config
                exit 1
            fi
        fi

            if [[ $line_number == "end" ]]
        then
            cat <<EOF
            *********************************************

            Successfully Installed Batsim and Batsched!!!

            *********************************************

            You will want to make sure .../basefiles/batsim_environment.sh is edited with options you need
            At a bare minimum set prefix=? to the correct prefix. This is probably going to be the full path to your simulator folder.
EOF
        fi


    done
    if [ $withGui = true ];then
        deployGui 
    fi
    exit 0
fi
if [ $FORMAT = 'charliecloud' ] && [ $NO = true ] && [ $PACK = true ];then
    basefiles=$MY_PATH
    deactivate
    cd ../
    prefix=${MY_PATH%/basefiles}
    mkdir python_env && cd python_env
    python3 -m venv ./
    . ./bin/activate
    python_prefix=$prefix/python_env
    python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip
    python3 -m pip install meson
    python3 -m pip install ninja
    python3 -m pip install pandas
    python3 -m pip install numpy
    python3 -m pip install seaborn
    python3 -m pip install shapely
    python3 -m pip install requests
    python3 -m pip install venv-pack
    export python3_ver=`python3 --version | awk '{print $2}' | awk -F. '{print $1"."$2}'`
    export file="$python_prefix/lib/python${python3_ver}/site-packages/mesonbuild/backend/backends.py"
    sed -i 's/\(if delta > \)\([0-9]\+[.][0-9]\+\)\(.*\)/\15.0\3/g' $file
    venv-pack -o $prefix/python_env.tar.gz
    cd $basefiles/CharlieCloud_compile
    rm -rf ./download ./boost_1_75_0
    rm -rf $basefiles/charliecloud
    rm -rf $prefix/batsim_ch
    mkdir $basefiles/charliecloud
    cd $basefiles/charliecloud
    url=$(curl -s https://api.github.com/repos/hpc/charliecloud/releases/latest | grep "browser_download_url" | awk -F: '{print $2":"$3}'| sed 's/\"//g')
    wget $url
    myFile=`basename $url`
    tar -xf $myFile
    mv ${myFile%.tar.gz} ./charliecloud
    mv $myFile ./charliecloud.tar.gz
    echo ${myFile%.tar.gz} > charliecloudName.txt
    cd charliecloud
    ./configure
    make
    cd ./bin
    export PATH=`pwd`:$PATH
    cd $basefiles/CharlieCloud_compile
    wget --no-check-certificate https://sourceforge.net/projects/boost/files/boost/1.75.0/boost_1_75_0.tar.gz/download
    tar -xf ./download
    chmod -R 777 ./boost_1_75_0
    export CH_IMAGE_STORAGE=`pwd`/$USER.ch
    rm -rf $CH_IMAGE_STORAGE
    ch-image delete batsim
    ch-image build --force --no-cache -t batsim -f Dockerfile ./
    ch-convert batsim $prefix/batsim_ch.tar.gz
    rm -rf $basefiles/charliecloud/charliecloud
    cd $prefix
    mkdir experiments
    mkdir configs
    rm -rf $prefix/python_env
    cd $prefix/..
    cp $basefiles/deploy.sh ./
    tar -czf batsim.tar.gz ./$(basename $prefix)
    mkdir -p batsim_packaged
    mv batsim.tar.gz ./batsim_packaged/
    mv deploy.sh ./batsim_packaged/
    echo $(basename $prefix) > ./batsim_packaged/prefixName.txt
    echo "Finished making your packaged directory"
    echo "copy $(dirname $prefix)/batsim_packaged folder over to computer with no internet"
    echo "then run this same script with un-package argument"
exit 0
fi
if [ $FORMAT = 'charliecloud' ] && [ $NO = true ] && [ $UNPACK = true ];then
    pack_prefix=$MY_PATH
    prefixName=`cat $pack_prefix/prefixName.txt`
    tar -xf batsim.tar.gz
    prefix=$pack_prefix/$prefixName
    cd $prefix
    mkdir python_env
    mv python_env.tar.gz $prefix/python_env
    cd $prefix/python_env
    tar -xf python_env.tar.gz
    if [ -d ./python_env ];then
        mv ./python_env $prefix/python_tmp
        rm -rf $prefix/python_env
        mv $prefix/python_tmp $prefix/python_env
    fi
    cd $prefix
    mkdir batsim_ch
    cd batsim_ch
    tar -xf $prefix/batsim_ch.tar.gz
    basefiles=$prefix/basefiles
    cd $prefix/basefiles/charliecloud
    tar -xf charliecloud.tar.gz
    myFile=`cat ./charliecloudName.txt`
    mv $myFile ./charliecloud
    cd ./charliecloud
    ./configure
    make
    cd $basefiles
    mv $basefiles/charliecloud $prefix/charliecloud
    export PATH=$prefix/charliecloud/charliecloud/bin:$PATH
    cd $basefiles
    cat <<EOF
*****************************************
        un-packing done!
*****************************************

You may want to run some tests using .../basefiles/tests/charliecloud/tests.sh
You will want to add anything relevant to .../basefiles/batsim_environment.sh  as well
At a bare minimum set prefix=? to the correct prefix. This is probably going to be your simulator folder.
EOF
exit 0
fi

if [ $FORMAT = 'charliecloud' ] && [ $NO = false ]; then
basefiles=$MY_PATH
deactivate
cd ../
mkdir python_env && cd python_env
python3 -m venv ./
. ./bin/activate
python3 -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --upgrade pip
python3 -m pip install meson
python3 -m pip install ninja
python3 -m pip install pandas
python3 -m pip install numpy
python3 -m pip install seaborn
python3 -m pip install shapely
python3 -m pip install requests
python3 -m pip install venv-pack

cd $basefiles/CharlieCloud_compile
rm -rf ./download ./boost_1_75_0
rm -rf ../charliecloud
rm -rf ../../batsim_ch
mkdir ../charliecloud
cd ../charliecloud
url=$(curl -s https://api.github.com/repos/hpc/charliecloud/releases/latest | grep "browser_download_url" | awk -F: '{print $2":"$3}'| sed 's/\"//g')
wget $url
myFile=`basename $url`
tar -xf $myFile
mv ${myFile%.tar.gz} ./charliecloud
cd charliecloud
./configure
make
cd ./bin
export PATH=`pwd`:$PATH
cd $basefiles/CharlieCloud_compile
wget --no-check-certificate https://sourceforge.net/projects/boost/files/boost/1.75.0/boost_1_75_0.tar.gz/download
tar -xf ./download
chmod -R 777 ./boost_1_75_0
export CH_IMAGE_STORAGE=`pwd`/$USER.ch
rm -rf $CH_IMAGE_STORAGE
ch-image delete batsim
if [ $withGUI = true ];then
    ch-image build --force --no-cache -t batsim -f DockerFile ./DockerfileGUI
fi
ch-image build --force --no-cache -t batsim -f Dockerfile ./
ch-convert batsim ${basefiles%/basefiles}/batsim_ch
cd ${basefiles%/basefiles}
mkdir -p experiments
mkdir -p configs
cd $basefiles
mv ./charliecloud ../
 cat <<EOF
*****************************************
        Deployment Finished
*****************************************

You may want to run some tests using .../basefiles/tests/charliecloud/tests.sh
You will want to add anything relevant to .../basefiles/batsim_environment.sh  as well
At a bare minimum set prefix=? to the correct prefix. This is probably going to be your 'simulator' folder.
EOF
exit 0
fi

if [ $FORMAT = 'docker' ]; then
#!/bin/bash
cd ./Docker_compile
wget --no-check-certificate https://sourceforge.net/projects/boost/files/boost/1.75.0/boost_1_75_0.tar.gz/download
tar -xf ./download
chmod -R 777 ./boost_1_75_0
docker build --no-cache -t simulator_compile .
cat <<EOF
*****************************************
        Deployment Finished
*****************************************

You may want to run some tests using /home/sim/simulator/basefiles/tests/docker/tests.sh
You will want to add anything relevant to .../basefiles/batsim_environment.sh as well
At a bare minimum set prefix=? to the correct prefix. This is probably going to be your /home/sim/simulator folder.
EOF
exit 0
fi
