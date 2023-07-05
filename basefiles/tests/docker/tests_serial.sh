#!/bin/bash
MY_PATH="$(dirname -- "${BASH_SOURCE[0]}")"
MY_PATH="$(cd -- "$MY_PATH" && pwd)"
MY_PATH=${MY_PATH%/tests/docker}
experiments=${MY_PATH%/basefiles}/experiments
rm -r $experiments/test_if_works_docker
$MY_PATH/myBatchTasks.sh -f $MY_PATH/tests/charliecloud/test_if_works.config -o test_if_works_docker -m docker -p none
file1_post=$MY_PATH/../experiments/test_if_works_docker/grizzly_resv_1/experiment_1/id_1/Run_1/output/expe-out/post_out_jobs.csv
compare1_post=$MY_PATH/tests/charliecloud/data/test_if_works/grizzly_resv_1/post_out_jobs.csv
file2_post=$MY_PATH/../experiments/test_if_works_docker/grizzly_resv_2/experiment_1/id_1/Run_1/output/expe-out/post_out_jobs.csv
compare2_post=$MY_PATH/tests/charliecloud/data/test_if_works/grizzly_resv_2/post_out_jobs.csv

diff $file1_post $compare1_post
comparison_1_post=$?

diff $file2_post $compare2_post
comparison_2_post=$?
addition=$(( $comparison_1_post + $comparison_2_post ))
if [ $addition -eq 0 ];then
cat <<"EOF"
********************************************
        SUCCESS DOCKER SERIAL
********************************************

EOF
else
cat <<EOF
**************  FAILURE WITH TESTS *************
comparison_1_post   = $comparison_1_post
comparison_2_post   = $comparison_2_post
EOF
fi

