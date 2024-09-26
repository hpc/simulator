#!/bin/bash
VALID_ARGS=$(getopt -o cf:p:ho:dm: --long modules,clean,format:,path:,only:,debug,help -- "$@")
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
BUILDTYPE="release"
ONLY="both"
modules=false
SRC_PATH=false
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
    -p | --path)
        SRC_PATH="$2"
        shift 2
        ;;
    -o | --only)
        ONLY="$2"
        shift 2
        ;;
    -m | --modules)
        modules="$2"
        shift 2
        ;;
    -d | --debug)
        BUILDTYPE="debug"
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

if [ $HELP = true ] || [ $FORMAT = false ] ;then
   

    cat <<"EOF"


    
Usage:
    compile.sh -f <STR> [-p <STR>] [-o <STR>] [-d]
    compile.sh --clean
    compile.sh --help

Required Options 1:

    -f, --format <STR>              The format to build things for:
                                    bare-metal | charliecloud | docker

Optional Options 1:

    -p, --path <STR>                The path to batsim/batsched folders,otherwise will use inplace default locations


    -o, --only <STR>                only compile:
                                    batsim | batsched | both
                                    [default: both]
    -m, --modules <STR>             Load modules in comma seperated STR
                                    ' example: --modules "gcc/10.3.0,cmake/3.22.3"


    -d, --debug                     compile with debugging and profiling

Required Options 2:

    -c, --clean                     Will clean up the basefiles folder from a previous build

Required Options 3:

    -h, --help                      Display this usage page

EOF
    exit 1
fi
if [ $modules != false ];then
    for i in $(echo $modules | tr "," "\n");do
        module load "$i"
    done
fi
prefix=${MY_PATH%/basefiles}
if [ $FORMAT == "charliecloud" ];then
    ch_bin=$prefix/charliecloud/charliecloud/bin
    ch_loc=$prefix/batsim_ch
    if [ $SRC_PATH != false ]; then
        rm -rf $ch_loc/home/sim/simulator/Downloads/batsim4
        rm -rf $ch_loc/home/sim/simulator/Downloads/batsched4
        cp -R $SRC_PATH/batsim4 $ch_loc/home/sim/simulator/Downloads/batsim4
        cp -R $SRC_PATH/batsched4 $ch_loc/home/sim/simulator/Downloads/batsched4
    else
        rm -rf $ch_loc/home/sim/simulator/Downloads/batsim4/build
        rm -rf $ch_loc/home/sim/simulator/Downloads/batsched4/build
    fi
    python_prefix=/home/sim/simulator/python_env
    install_prefix=/home/sim/simulator/Install
    if [[ $ONLY == "both" ]] || [[ $ONLY == "batsim" ]];then
        $ch_bin/ch-run $ch_loc --write  -- /bin/bash -c "source /home/sim/.environ; cd /home/sim/simulator/Downloads/batsim4;source /home/sim/simulator/python_env/bin/activate; $python_prefix/bin/meson build --prefix=$install_prefix --buildtype $BUILDTYPE;$python_prefix/bin/ninja -C build;$python_prefix/bin/meson install -C build "
    fi
    if [[ $ONLY == "both" ]];then
        sleep 15
    fi
    if [[ $ONLY == "both" ]] || [[ $ONLY == "batsched" ]];then
        $ch_bin/ch-run $ch_loc --write  -- /bin/bash -c "source /home/sim/.environ; cd /home/sim/simulator/Downloads/batsched4;source /home/sim/simulator/python_env/bin/activate; $python_prefix/bin/meson build --prefix=$install_prefix --buildtype $BUILDTYPE;$python_prefix/bin/ninja -C build;$python_prefix/bin/meson install -C build "
    fi
    exit 0
fi
if [ $FORMAT == "docker" ]; then
    prefix=/home/sim/simulator
    rm -rf $prefix/Downloads/batsim4/build
    rm -rf $prefix/Downloads/batsched4/build
    python_prefix=$prefix/python_env
    install_prefix=$prefix/Install
    export PKG_CONFIG_PATH=$install_prefix/lib/pkgconfig:$install_prefix/lib64/pkgconfig:$install_prefix/lib/x86_64-linux-gnu/pkgconfig
    export BOOST_ROOT=$install_prefix
    source /home/sim/.bashrc
    source $python_prefix/bin/activate

    if [[ $ONLY == "both" ]] || [[ $ONLY == "batsim" ]];then
    cd $prefix/Downloads/batsim4
    $python_prefix/bin/meson build --prefix=$install_prefix --buildtype $BUILDTYPE
    $python_prefix/bin/ninja -C build
    $python_prefix/bin/meson install -C build
    fi
    if [[ $ONLY == "both" ]];then
        sleep 15
    fi
    if [[ $ONLY == "both" ]] || [[ $ONLY == "batsched" ]];then
    cd $prefix/Downloads/batsched4
    $python_prefix/bin/meson build --prefix=$install_prefix --buildtype $BUILDTYPE
    $python_prefix/bin/ninja -C build
    $python_prefix/bin/meson install -C build
    fi
    exit 0
fi
if [ $FORMAT == "bare-metal" ]; then
    source $prefix/basefiles/batsim_environment.sh
    if [ $SRC_PATH != false ];then
        rm -rf $downloads_prefix/batsim4
        rm -rf $downloads_prefix/batsched4
        cp -R $SRC_PATH/batsim4 $downloads_prefix/
        cp -R $SRC_PATH/batsched4 $downloads_prefix/
    else
        rm -rf $downloads_prefix/batsim4/build
        rm -rf $downloads_prefix/batsched4/build
    fi
    export PKG_CONFIG_PATH=$install_prefix/lib/pkgconfig:$install_prefix/lib64/pkgconfig:$install_prefix/lib/x86_64-linux-gnu/pkgconfig
    export BOOST_ROOT=$install_prefix

    if [[ $ONLY == "both" ]] || [[ $ONLY == "batsim" ]];then
    cd $downloads_prefix/batsim4
    $python_prefix/bin/meson build --prefix=$install_prefix --buildtype $BUILDTYPE
    $python_prefix/bin/ninja -C build
    $python_prefix/bin/meson install -C build
    fi
    if [[ $ONLY == "both" ]];then
        sleep 15
    fi
    if [[ $ONLY == "both" ]] || [[ $ONLY == "batsched" ]];then
    cd $prefix/Downloads/batsched4
    $python_prefix/bin/meson build --prefix=$install_prefix --buildtype $BUILDTYPE
    $python_prefix/bin/ninja -C build
    $python_prefix/bin/meson install -C build
    fi
    exit 0
fi


