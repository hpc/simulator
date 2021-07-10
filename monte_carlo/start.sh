export MODULEPATH=/opt/ohpc/admin/modulefiles:/opt/ohpc/pub/modulefiles:/ac-project/software/modules/linux-centos7-x86_64/Core/linux-centos7-ivybridge && \
module --ignore-cache load gcc/10.2.0 && \
module --ignore-cache load cmake/3.15.4 && \
export PATH=$PATH:/home/cwalker/Install/bin:/home/cwalker/Downloads/goroot/bin/:/home/cwalker/go/bin/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/cwalker/Install/lib:/home/cwalker/Install/lib64
export LMOD_SH_DBG_ON=1
source /home/cwalker/python_env/bin/activate
