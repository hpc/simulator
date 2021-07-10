#!/bin/bash
export PKG_CONFIG_PATH=/home/$USER/Install/lib/pkgconfig:/home/$USER/Install/lib64/pkgconfig && \
export MODULEPATH=/opt/ohpc/admin/modulefiles:/opt/ohpc/pub/modulefiles:/ac-project/software/modules/linux-centos7-x86_64/Core/linux-centos7-ivybridge && \
export PATH=$PATH:/home/$USER/Install/bin:/home/$USER/Downloads/goroot/bin && \
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/home/$USER/Install/ac-project/software/linux-centos7-ivybridge/gcc-4.8.5/gcc-10.2.0/lib64\:/ac-project/software/linux-centos7-ivybridge/gcc-4.8.5/gcc-10.2.0/lib/pkgconfig/
module load gcc/10.2.0 && \
module load cmake/3.15.4 && \
mkdir Downloads && \
mkdir Install && \
mkdir python_env && \
cd Downloads && \
wget https://sourceforge.net/projects/boost/files/boost/1.75.0/boost_1_75_0.tar.gz/download && \
tar -xf ./download && \
cd ./boost_1_75_0/ && \
./bootstrap.sh --prefix=/home/$USER/Install && \
./b2 install && \

#### don't need to compile Cmake since we are loading cmake above
#cd /home/$USER/Downloads/ && \
#git clone https://github.com/Kitware/CMake.git &&
#cd ./CMake && \
#git checkout tags/v3.18.4 -b our_v3.18.4d && \
#./bootstrap --prefix=/home/$USER/Install -- -DCMAKE_USE_OPENSSL:BOOL=OFF && \
#gmake && \
#gmake install && \

cd /home/$USER/Downloads/ && \
git clone https://framagit.org/simgrid/simgrid.git && \
cd /home/$USER/Downloads/simgrid/ && \
git checkout tags/v3.25 -b our_v3.25d
cmake -DBOOST_ROOT="/home/$USER/Install" -DCMAKE_INSTALL_PREFIX="/home/$USER/Install" /home/$USER/Downloads/simgrid/  \
    -Denable_documentation=off \
    -Denable_java=off \
    -Denable_msg=off \
    -Denable_fortran=off \
    -Denable_model-checking=off \
    -Denable_ns3=off \
    -Denable_lua=off \
    -Denable_lib_in_jar=off \
    -Denable_maintainer_mode=off \
    -Denable_mallocators=on \
    -Denable_debug=off \
    -Denable_smpi=on \
    -Dminimal-bindings=on \
    -Denable_smpi_ISP_testsuite=off \
    -Denable_smpi_MPICH3_testsuite=off \
    -Denable_compile_warnings=off \
    -Denable_compile_optimizations=on \
    -Denable_lto=on && \
make && \
make install && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/zeromq/libzmq.git && \
cd /home/$USER/Downloads/libzmq && \
git checkout tags/v4.3.3 -b our_v4.3.3d && \
./autogen.sh && \
./configure --prefix=/home/$USER/Install/ && \
make && \
make install && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/redis/hiredis.git && \
cd ./hiredis && \
git checkout tags/v0.14.0 -b our_v0.14.0d &&\
make PREFIX=/home/$USER/Install && \
make PREFIX=/home/$USER/Install install && \
printf "%s%s%s%s" "prefix=/home/$USER/Install
exec_prefix="'${prefix}'"
libdir=/home/$USER/Install/ac-project/software/linux-centos7-ivybridge/gcc-4.8.5/gcc-10.2.0/lib64:/ac-project/software/linux-centos7-ivybridge/gcc-4.8.5/gcc-10.2.0/lib
includedir=/home/$USER/Install/include/hiredis

Name: hiredis
Description: Minimalistic C client library for Redis.
Version: 0.14.0"'
Libs: -L${libdir} -lhiredis
Cflags: -I${includedir} -D_FILE_OFFSET_BITS=64'> /home/$USER/Install/lib/pkgconfig/hiredis.pc && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/enki/libev.git && \
cd ./libev && \
./configure --prefix=/home/$USER/Install && \
make && \
make install && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/alisw/GMP.git && \
cd ./GMP && \
./configure --prefix=/home/$USER/Install && \
make && \
make install && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/zeromq/cppzmq.git && \
cd ./cppzmq && \
cmake -DCMAKE_PREFIX_PATH="/home/$USER/Install/" -DCMAKE_INSTALL_PREFIX="/home/$USER/Install" ./ && \
make && \
make install && \
cd /home/$USER/python_env/ && \
python3 -m venv ./ && \
source "/home/$USER/python_env/bin/activate" && \
python3 -m pip install meson && \
python3 -m pip install ninja && \
python3 -m pip install pandas && \
python3 -m pip install seaborn && \
python3 -m pip install shapely && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/golang/go.git && \
cd go && \
git checkout origin/release-branch.go1.4 -b our_go1.4d && \
export CGO_ENABLED=0 && \
cd src && \
./make.bash && \
cd /home/$USER/ && \
mv /home/$USER/Downloads/go ./go1.4 && \
cd /home/$USER/Downloads && \
git clone https://go.googlesource.com/go goroot && \
cd ./goroot && \
git checkout go1.16 -b our_go1.16d && \
cd src && \
./make.bash && \
export PATH=$PATH:/home/$USER/Install/bin:/home/$USER/Downloads/goroot/bin && \
cp /home/$USER/Install/ac-project/software/linux-centos7-ivybridge/gcc-4.8.5/gcc-10.2.0/lib64\:/ac-project/software/linux-centos7-ivybridge/gcc-4.8.5/gcc-10.2.0/lib/*.* /home/$USER/Install/lib/ && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/mpoquet/redox.git && \
cd /home/$USER/Downloads/redox/ && \
git checkout install-pkg-config-file && \
mkdir build && cd build && \
cmake -DHIREDIS_INCLUDE_DIR="/home/$USER/Install/include/" -DHIREDIS_LIBRARY="/home/$USER/Install/lib/" -DLIBEV_INCLUDE_DIR="/home/$USER/Install/include/" -DLIBEV_LIBRARY="/home/$USER/Install/lib" -DCMAKE_INSTALL_PREFIX=/home/$USER/Install /home/$USER/Downloads/redox/ && \
make && \
cd /home/$USER/Downloads/redox/build/ && \
make install 
cd /home/$USER/Downloads/ && \
git clone https://github.com/Tencent/rapidjson.git && \
mkdir /home/$USER/Downloads/rapidjson/build && cd /home/$USER/Downloads/rapidjson/build && \
cmake -DCMAKE_INSTALL_PREFIX=/home/$USER/Install .. && \
make && \
make install && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/zeux/pugixml.git && \
cd /home/$USER/Downloads/pugixml && \
mkdir /home/$USER/Downloads/pugixml/build && \
cd /home/$USER/Downloads/pugixml/build && \
cmake -DCMAKE_INSTALL_PREFIX=/home/$USER/Install .. && \
make && \
make install && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/google/googletest.git && \
cd ./googletest && \
cmake -DCMAKE_INSTALL_PREFIX=/home/$USER/Install && \
make && \
make install && \
cd /home/$USER/Downloads && \
git clone https://framagit.org/batsim/intervalset.git && \
cd /home/$USER/Downloads/intervalset && \
export BOOST_ROOT=/home/$USER/Install && \
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/home/$USER/Install/lib64/pkgconfig && \
meson build --buildtype release --prefix /home/$USER/Install && \
cd /home/$USER/Downloads/intervalset/build/ && \
ninja && \
ninja install && \
cd /home/$USER/Downloads && \
git clone https://github.com/docopt/docopt.cpp.git && \
cd /home/$USER/Downloads/docopt.cpp/ && \
mkdir build && \
cd build && \
cmake -DCMAKE_INSTALL_PREFIX=/home/$USER/Install .. && \
make && \
make install && \
printf "%s%s" "libdir=/home/$USER/Install/lib
includedir=/home/$USER/Install/include

Name: GMP
Description: GNU Multiple Precision
Version: 10.3.2

Libs: -L" '${libdir} -lgmp
Cflags: -I${includedir}'> /home/$USER/Install/lib/pkgconfig/gmpxx.pc && \
printf "%s%s" "libdir=/home/$USER/Install/lib
includedir=/home/$USER/Install/include

Name: ev
Description: ev
Version: 1.0

Libs: -L" '${libdir} -lev
Cflags: -I${includedir}' > /home/$USER/Install/lib/pkgconfig/ev.pc && \
printf "%s%s" "libdir=/home/$USER/Install/lib
includedir=/home/$USER/Install/include

Name: Loguru
Description: Logging
Version: 1.2

Libs: -L" '${libdir} -lloguru -ldl
Cflags: -I${includedir}' > /home/$USER/Install/lib/pkgconfig/loguru.pc && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/oar-team/batsim.git && \
cd /home/$USER/Downloads/batsim && \
git checkout tags/v3.1.0 -b my_batsim && \
patch -p8 -i /home/$USER/Downloads/patch_batsim.patch && \
cd /home/$USER/Downloads/batsim && \
meson build --prefix=/home/$USER/Install --buildtype release && \
ninja -j 2 -C build && \
meson install -C build && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/emilk/loguru.git && \
cd /home/$USER/Downloads/loguru && \
g++ -std=c++11 -o libloguru.so -shared -pthread -fPIC loguru.cpp && \
cp /home/$USER/Downloads/loguru/libloguru.so /home/$USER/Install/lib/ && \
cp /home/$USER/Downloads/loguru/loguru.hpp /home/$USER/Install/include/ && \
export BOOST_ROOT=/home/$USER/Install && \
cd /home/$USER/Downloads/ && \
git clone https://github.com/oar-team/batsched.git && \
cd /home/$USER/Downloads/batsched && \
git checkout tags/v1.3.0 -b my_batsched && \
patch -p8 -i /home/$USER/Downloads/patch_batsched.patch 
meson build --prefix=/home/$USER/Install --buildtype release && \
ninja -j 2 -C build && \
meson install -C build && \
cd /home/$USER/Downloads/ && \
go get framagit.org/batsim/batexpe/cmd/robin && \
go get framagit.org/batsim/batexpe/cmd/robintest
