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

export basefiles_prefix=$prefix/basefiles
export install_prefix=$prefix/Install
export downloads_prefix=$prefix/Downloads
export python_prefix=$prefix/python_env

export PATH=$PATH:$prefix/charliecloud/charliecloud/bin:$basefiles_prefix:$install_prefix/bin:/usr/bin:/usr/sbin
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$install_prefix/lib:$install_prefix/lib64
export LMOD_SH_DBG_ON=1
source $python_prefix/bin/activate

