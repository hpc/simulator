#!/bin/bash
VALID_ARGS=$(getopt -o cf:p:h --long clean,format:,path:,help -- "$@")
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
    -p | --path)
        SRC_PATH="$2"
        shift 2
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

if [ $HELP = true ] || [ $FORMAT = false ] || [ $SRC_PATH = false ];then
   

    cat <<"EOF"


    
Usage:
    compile.sh -f <STR> -p <STR>
    compile.sh --clean
    compile.sh --help

Required Options 1:

    -f, --format <STR>              The format to build things for:
                                    bare-metal | charliecloud | docker

    -p, --path <STR>                The path to batsim/batsched folders

Required Options 2:

    -c, --clean                     Will clean up the basefiles folder from a previous build

Required Options 3:

    -h, --help                      Display this usage page

EOF
    exit 1
fi
prefix=${MY_PATH%/basefiles}
if [ $FORMAT == "charliecloud" ];then
    ch_bin=$prefix/charliecloud/charliecloud/bin
    ch_loc=$prefix/batsim_ch
    rm -rf $ch_loc/home/sim/simulator/Downloads/batsim4
    rm -rf $ch_loc/home/sim/simulator/Downloads/batsched4
    cp -R $SRC_PATH/batsim4 $ch_loc/home/sim/simulator/Downloads/batsim4
    cp -R $SRC_PATH/batsched4 $ch_loc/home/sim/simulator/Downloads/batsched4
    python_prefix=/home/sim/simulator/python_env
    install_prefix=/home/sim/simulator/Install
    $ch_bin/ch-run $ch_loc --write --set-env=HOME=/home/sim -- /bin/bash -c "export PKG_CONFIG_PATH=$install_prefix/lib/pkgconfig:$install_prefix/lib64/pkgconfig:$install_prefix/lib/x86_64-linux-gnu/pkgconfig;export BOOST_ROOT=$install_prefix;source /home/sim/.bashrc; cd /home/sim/simulator/Downloads/batsim4;source /home/sim/simulator/python_env/bin/activate; $python_prefix/bin/meson build --prefix=$install_prefix --buildtype release;$python_prefix/bin/ninja -C build;$python_prefix/bin/meson install -C build "
    $ch_bin/ch-run $ch_loc --write --set-env=HOME=/home/sim -- /bin/bash -c "export PKG_CONFIG_PATH=$install_prefix/lib/pkgconfig:$install_prefix/lib64/pkgconfig:$install_prefix/lib/x86_64-linux-gnu/pkgconfig;export BOOST_ROOT=$install_prefix;source /home/sim/.bashrc; cd /home/sim/simulator/Downloads/batsched4;source /home/sim/simulator/python_env/bin/activate; $python_prefix/bin/meson build --prefix=$install_prefix --buildtype release;$python_prefix/bin/ninja -C build;$python_prefix/bin/meson install -C build "
fi