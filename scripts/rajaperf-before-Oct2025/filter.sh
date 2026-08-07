#!/bin/bash

# Iterate though all the data directories and create filtered.txt


machines="boraxo catalyst corona ec2-c5n ec2-c6a ec2-c6i ec2-p3 ec2-p4d lassen mammoth pascal poodle quartz ruby tioga"

# RAJAPef '--repfact' argument used
rep=0.5

# RAJAPef '--sizefact' argument used
sz="0.5 1.0 2.0"

# For repeated number of experiments
repeats=`seq 1 3`

for s in ${sz}
do
  for m in ${machines}
  do
    for i_m in ${repeats}
    do
      if [ ! -d ${m}-${i_m} 2> /dev/null ] ; then
        echo "Directory ${m}-${i_m} does not exist!" > /dev/stderr
        continue
      fi
      pushd ${m}-${i_m} 2> /dev/null > /dev/null

      ff=`ls -1d rep${rep}-sz${s}* 2> /dev/null`
      for f in ${ff}
      do
        pushd ${f} 2> /dev/null > /dev/null
        ../../filter.awk RAJAPerf-timing-Average.csv > filtered.txt
        popd 2> /dev/null > /dev/null
      done
      popd 2> /dev/null > /dev/null
    done
  done
done
