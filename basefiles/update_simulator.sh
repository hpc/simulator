#!/usr/bin/bash
cd $prefix
cp $prefix/basefiles/batsim_environment.sh ../
git pull
rm $prefix/basefiles/batsim_environment.sh
mv ../batsim_environment.sh $prefix/basefiles/batsim_environment.sh
