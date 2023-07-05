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

#export prefix=?

#export SBATCH_PARTITION=standard
#export SBATCH_QOS=standard
#export SBATCH_NO_REQUEUE="yes"



export PATH=$PATH:$prefix/charliecloud/charliecloud/bin:$prefix/basefiles:$prefix/Install/bin:/usr/bin:/usr/sbin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$prefix/Install/lib:$prefix/Install/lib64
export LMOD_SH_DBG_ON=1
source $prefix/python_env/bin/activate

