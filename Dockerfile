 
FROM ubuntu:20.04

LABEL desc="Batsim simulator made ready"

# get the right repos
USER root
RUN \
    apt-get update && \
    groupadd ccu && \
    groupadd wheel && \
    useradd -d /home/sim -ms /bin/bash sim && \
    usermod -aG wheel sim && \
    usermod -aG ccu sim && \
    echo "sim:sim" | chpasswd && \
    echo "Added sim user" && \
    apt update && \
    DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata && \
    apt-get install build-essential -y && \
    apt-get install cmake libboost-all-dev python3.6 git-all meson -y
RUN \  
    apt-get update && \
    apt-get install libzmqpp-dev -y && \
    apt-get install libgmp-dev libzmq3-dev -y && \
    apt-get install libev-dev -y 
RUN \
    apt-get update && \
    apt-get install -y pkg-config
   
COPY ./redox.pc /usr/lib64/pkgconfig/redox.pc
COPY ./simgrid.pc /usr/lib64/pkgconfig/simgrid.pc
COPY ./loguru.pc /usr/lib64/pkgconfig/loguru.pc  
COPY ./gmpxx.pc /usr/lib64/pkgconfig/gmpxx.pc
COPY ./intervalset.pc /usr/lib64/pkgconfig/intervalset.pc
COPY ./ev.pc /usr/lib64/pkgconfig/ev.pc

USER sim

RUN \
    mkdir /home/sim/Downloads && \
    cd /home/sim/Downloads && \
    git clone https://github.com/redis/hiredis.git && \
    cd hiredis && \
    git checkout v0.14.0 -b our_v0.14.0&& \
    make
USER root
RUN \
    cd /home/sim/Downloads/hiredis/ && \
    make install



#install simgrid (current version 3.25)

RUN \
    cd /home/sim/Downloads/ && \
    git clone https://framagit.org/simgrid/simgrid.git && \
    cd /home/sim/Downloads/simgrid/ && \
    git checkout tags/v3.25 -b our_v3.25
RUN \
    cd /home/sim/Downloads/simgrid && \
    cmake -DCMAKE_INSTALL_PREFIX="/usr/local/" /home/sim/Downloads/simgrid/  \
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
    make
USER root
RUN \
    cd /home/sim/Downloads/simgrid/ && \
    make install
 

USER sim
RUN \
    cd /home/sim/Downloads/ && \
    git clone https://github.com/mpoquet/redox.git && \
    cd /home/sim/Downloads/redox/ && \
    git checkout install-pkg-config-file && \
    mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local/ /home/sim/Downloads/redox/ && \
    make
USER root
RUN \
    cd /home/sim/Downloads/redox/build/ && \
    make install 
USER sim
RUN \
    cd /home/sim/Downloads/ && \
    git clone https://github.com/Tencent/rapidjson.git && \
    mkdir /home/sim/Downloads/rapidjson/build && cd /home/sim/Downloads/rapidjson/build && \
    cmake .. && make
USER root
RUN \
    cd /home/sim/Downloads/rapidjson/build && \
    make install
USER sim
RUN \
    cd /home/sim/Downloads/ && \
    git clone https://github.com/zeux/pugixml.git && \
    cd /home/sim/Downloads/pugixml && \
    mkdir /home/sim/Downloads/pugixml/build && \
    cd /home/sim/Downloads/pugixml/build && cmake .. && \
    make
USER root
RUN \
    cd /home/sim/Downloads/pugixml/build/ && \
    make install 
    
USER sim
RUN \
    cd /home/sim/Downloads/ && \
    git clone https://framagit.org/batsim/intervalset.git && \
    cd /home/sim/Downloads/intervalset && \
    meson build --buildtype release && \
    cd /home/sim/Downloads/intervalset/build/ && \
    ninja
USER root
RUN \
    cd /home/sim/Downloads/intervalset/build/ && \
    ninja install
USER sim
RUN \
    cd /home/sim/Downloads && \
    git clone https://github.com/docopt/docopt.cpp.git && \
    cd /home/sim/Downloads/docopt.cpp/ && \
    mkdir build && cd build && \
    cmake .. && make
USER root
RUN \
    cd /home/sim/Downloads/docopt.cpp/build/ && \
    make install
    

ENV PKG_CONFIG_PATH=/usr/local/lib64/pkgconfig/:/usr/lib64/pkgconfig/
RUN rm /usr/lib64/pkgconfig/redox.pc
USER sim 
COPY ./patch_batsim.patch /home/sim/Downloads/patch_batsim.patch
COPY ./patch_batsched.patch /home/sim/Downloads/patch_batsched.patch
RUN \
    cd /home/sim/Downloads/ && \
    git clone https://github.com/oar-team/batsim.git && \
    cd /home/sim/Downloads/batsim && \
    git checkout tags/v3.1.0 -b my_batsim && \
    patch -p8 -i /home/sim/Downloads/patch_batsim.patch
RUN \
    cd /home/sim/Downloads/ && \
    git clone https://github.com/oar-team/batsched.git && \
    cd /home/sim/Downloads/batsched && \
    git checkout tags/v1.3.0 -b my_batsched && \
    patch -p8 -i /home/sim/Downloads/patch_batsched.patch 
RUN \
    cd /home/sim/Downloads/batsim && \
    meson build --prefix=/usr/local/ --buildtype release && \
    ninja -j 2 -C build
    #mkdir /home/sim/Downloads/batsim/build && cd /home/sim/Downloads/batsim/build && \
    #
    #cmake -DCMAKE_PREFIX_PATH=/usr/local /home/sim/Downloads/batsim/ && make
USER root
RUN \
    cd /home/sim/Downloads/batsim && \
    meson install -C build
USER sim
RUN\
    cd /home/sim/Downloads/ && \
    git clone https://github.com/emilk/loguru.git && \
    cd /home/sim/Downloads/loguru && \
    g++ -std=c++11 -o libloguru.so -shared -pthread -fPIC loguru.cpp
USER root
RUN \
    cp /home/sim/Downloads/loguru/libloguru.so /lib/ && \
    cp /home/sim/Downloads/loguru/loguru.hpp /usr/include/  
    
#RUN \
 #   find /usr/local/lib64/pkgconfig/ -name "*.pc" -print | xargs -I{} cp {} /usr/lib64/pkgconfig/ && \
  #  find /usr/local/lib/pkgconfig/ -name "*.pc" -print | xargs -I{} cp {} /usr/lib64/pkgconfig/ 

USER sim
RUN \
    cd /home/sim/Downloads/batsched && \
    meson build --prefix=/usr/local/ --buildtype release && \
    ninja -j 2 -C build
USER root
RUN \
    cd /home/sim/Downloads/batsched/ && \
    meson install -C build     
USER root
RUN  apt-get update && apt-get install golang -y
USER sim
RUN \
    cd /home/sim/Downloads/ && \
    go get framagit.org/batsim/batexpe/cmd/robin && \
    go get framagit.org/batsim/batexpe/cmd/robintest

USER root
RUN \
    apt-get update && \
    apt-get install -y nano vim python3-pip  && \
    python3 -m pip install pandas numpy
RUN \
    echo "root:root"| chpasswd 
USER sim
RUN mkdir /home/sim/experiments
USER root
RUN apt-get update && apt-get install iproute2 -y

COPY ./.rootbashrc /root/.bashrc
USER sim
COPY ./.bashrc /home/sim/.bashrc
USER sim
COPY ./basefiles /home/sim/basefiles
COPY ./basefiles/sweeps /home/sim/basefiles/sweeps
COPY ./basefiles/workload_types /home/sim/basefiles/workload_types
COPY ./basefiles/platforms /home/sim/basefiles/platforms
USER root
RUN chown -R sim:sim /home/sim/basefiles
USER sim
WORKDIR /home/sim/basefiles
CMD ["/bin/bash"]
