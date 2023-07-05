#!/bin/bash
curDir=`pwd`
export PATH=${curDir%/basefiles}/charliecloud/charliecloud/bin:$PATH
ch-run ../batsim_ch --bind ${curDir%/basefiles}:/mnt/  --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/basefiles;source /home/sim/python_env/bin/activate; python3 generate_config_docker.py -i /mnt/basefiles/tests/charliecloud/test1_consv_bf_resv.config -o /mnt/experiments/test1 --output-config"
ch-run ../batsim_ch --bind ${curDir%/basefiles}:/mnt/  --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/basefiles;source /home/sim/python_env/bin/activate; python3 run-experiments_docker.py -i /mnt/experiments/test1 --socket-start 12000"


#ch-run ../batsim_ch --bind ${curDir%/basefiles}:/mnt/  --write --set-env=HOME=/home/sim -- /bin/bash -c "source /home/sim/.bashrc; cd /mnt/basefiles;source /home/sim/python_env/bin/activate; python3 generate_config_docker.py -i /mnt/basefiles/tests/charliecloud/test1_consv_bf_resv.config -o /mnt/experiments/test1_slurm --output-config"
#python3 run-experiments_charliecloud_slurm.py --input $1 --input-ch /mnt/experiments/test1_slurm --socket-start 12000
