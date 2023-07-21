#!/bin/bash
VALID_ARGS=$(getopt -o f:npux:l:c --long clean,format:,no-internet,package,un-package,prefix:,line-number:,help -- "$@")
if [[ $? -ne 0 ]]; then
    exit 1;
fi
MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
MY_PATH="$(cd -- "$MY_PATH" && pwd)"


FORMAT=false
NO=false
PACK=false
UNPACK=false
PREFIX=false
LINE=false
HELP=false
CLEAN=false
eval set -- "$VALID_ARGS"
while true; do
  case "$1" in
    -c | --clean)
        CLEAN=true
        shift 1
        ;;
    -f | --format)
        FORMAT="$2"
        shift 2
        ;;
    -x | --prefix)
        PREFIX="$2"
        shift 2
        ;;
    -l | --line-number)
        LINE="$2"
        shift 2
        ;;
    -n | --no-internet)
        NO=true
        shift 1
        ;;
    -p | --package)
        PACK=true
        shift 1
        ;;
    -u | --un-package)
        UNPACK=true
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
if [ $CLEAN = false ]; then
if [ $HELP = true ] || [ $FORMAT = false ] || \
    ([ $FORMAT != 'bare-metal' ] && ( [ $PREFIX != false ] || [ $LINE != false ] )) || \
    ([ $FORMAT != 'charliecloud' ] && [ $FORMAT != 'bare-metal' ] && [ $FORMAT != 'docker' ]) || \
    ([ $FORMAT != 'charliecloud' ] && ( [ $NO = true ] || [ $PACK = true ] || [ $UNPACK = true ]) ) || \
    ([ $FORMAT == 'charliecloud' ] && ( [ $NO = false ] && ( [ $PACK = true ] || [ $UNPACK = true ]) ) ) || \
    ([ $FORMAT == 'charliecloud' ] && [ $NO = true ] && ( ([ $PACK = true ] && [ $UNPACK = true ] ) || ( [ $PACK = false ] && [ $UNPACK = false ]))) ;then

    cat <<"EOF"


    deploy.sh               automates the downloading compiling and building of batsim into different formats and in different conditions.
                            NOTE: For charliecloud and bare-metal, gcc,make,cmake,python3 etc... is assumed to be working and a recent version.

Usage:
    deploy.sh -f <STR>  [-x][-l]  [--no-internet ( [-p] | [-u] )]
    deploy.sh --clean

Required Options 1:

    -f, --format <STR>              The format to build things for:
                                    bare-metal | charliecloud | docker
Required Options 2:

    -c, --clean                     Will clean up the basefiles folder from a previous deploy

Optional Options 1:
    -x, --prefix  <STR>             Only used with --format=bare-metal.
                                    The full path to the folder that everything is going to install to

    -l, --line-number <INT>         Only used with --format=bare-metal.
                                    The line number into deploy_commands to start at.

    -n, --no-internet               Only used with --format=charliecloud
                                    If set, will package a folder up that you can then move to
                                    the computer with no internet.  The folder is about a 3.5GB
                                    folder with tar.gz files inside.
                                    Must use -p or -u options with this.

    -p, --package                   Only used with --no-internet.
                                    Will initiate the packaging of batsim

    -u, --un-package                Only used with --no-internet.
                                    Will initiate the un-packaging of batsim.

    -h, --help                      Display this usage page

EOF
    exit 1
fi
fi
if [ $CLEAN = true ];then
    basefiles=$MY_PATH
    rm -rf $basefiles/CharlieCloud_compile/download $basefiles/CharlieCloud_compile/boost_1_75_0
    rm -rf $basefiles/charliecloud
    rm -rf $basefiles/Docker_compile/download $basefiles/Docker_compile/boost_1_75_0
    rm -f $basefiles/deploy.config
    exit 0
fi

if [ $FORMAT = 'bare-metal' ];then

    myDir=$MY_PATH
    echo "myDir=$myDir"
    touch $myDir/deploy.config
    line_number=`sed -n 1p $myDir/deploy.config`
    end_line=`cat $myDir/deploy_commands | wc -l`
    if [ $LINE = false ]
    then
        if [ $PREFIX = false ]
        then
        echo "Enter the absolute folder you want to download and install things to:"
        read prefix
        else
        prefix=$PREFIX
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
            echo "Enter the absolute folder you want to download and install things to:"
            read prefix
            else
            prefix=$PREFIX
        fi
        mkdir -p $prefix
        echo $line_number > $myDir/deploy.config
        echo "$prefix" >> $myDir/deploy.config
    fi
    source genPrefix
    mkdir -p $downloads_prefix && \
    mkdir -p $install_prefix && \
    mkdir -p $python_prefix && \
    oneliner=1
    for i in `seq $line_number 1 $end_line`
    do
        if [[ $oneliner -eq 0 ]]
        then
            line=`tr -d '\\' <<< $line`
            current=`sed -n ${i}p $myDir/deploy_commands`
            line="$line $current"
        else
            line=`sed -n ${i}p $myDir/deploy_commands`
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
        eval "$line"
        if [[ $line_number != "boost" ]]
        then

            if [[ $? -eq 1 ]]
            then

                echo "Error after line_number: $line_number"
                echo "Try to fix error and start this script again. Exiting..."
                echo "$line_number" > $myDir/deploy.config
                echo "$prefix" >> $myDir/deploy.config
                exit 1
            fi
        fi

            if [[ $line_number -eq "end" ]]
        then
            cat <<EOF
            *********************************************

            Successfully Installed Batsim and Batsched!!!

            *********************************************

            You will want to add this to your basefiles/batsim_environment.sh file:
EOF
            printf "\n\n%s\n\n" "export prefix=$prefix"
        fi


    done
exit 0
fi
if [ $FORMAT = 'charliecloud' ] && [ $NO = true ] && [ $PACK = true ];then
    basefiles=$MY_PATH
    deactivate
    cd ../
    prefix=${MY_PATH%/basefiles}
    mkdir python_env && cd python_env
    python3 -m venv ./
    source ./bin/activate
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
EOF
exit 0
fi

if [ $FORMAT = 'charliecloud' ] && [ $NO = false ]; then
#!/bin/bash
basefiles=$MY_PATH
deactivate
cd ../
mkdir python_env && cd python_env
python3 -m venv ./
source ./bin/activate
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
EOF
exit 0
fi
