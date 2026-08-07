#!/bin/bash

# This script dentifies which job has failed or is incomplete,
# by scanning through all the runs with various argument choices
# of a particular app and a number of ranks, under machine/app/ranks

# range of per-argument job directories
a_1=1
a_n=186

# range of repeated runs
r_1=1
r_n=3

if [ $# -eq 1 ] ; then
  a_n=$1
fi

app_dir=`pwd | rev | cut -d '/' -f 2 | rev`

for a in `seq ${a_1} ${a_n}`
do
  if [ ! -d arg_${a} ] ; then
    echo "no more run for arg_${a}"
    break
  fi
  pushd arg_${a} 2> /dev/null > /dev/null

  for r in `seq ${r_1} ${r_n}`
  do
    # Count how many redundant output files exist
    fcnt=`ls -1 out-*-${r}.txt 2> /dev/null | wc -l`
    if [ ${fcnt} -eq 0 ] ; then
      # No output file exists
      echo arg_${a}/${r} not run
      break
    elif [ ${fcnt} -gt 1 ] ; then
      # move the reduntant output files to a subfolder 'old'
      echo redundant output files in `pwd`:
      ls -1 out-*-${r}.txt

      mkdir -p old
      counter=1
      while [ ${counter} -lt ${fcnt} ] ; do
        ((counter++))
        rf_1=`ls -1 out-*-${r}.txt | head -n 1`
        mv ${rf_1} old
      done
    fi

    # Get the name of the only file left
    rf=`ls -1 out-*-${r}.txt | tail -n 1`
    duration=`tail -n 1 $rf | grep DURATION | awk '{print $2}'`
    ok="1"
    
    # Application-specific completion test
    if [ "${app_dir}" == "amg" ] ; then
      ok=`tail -n 4 $rf | head -n 2 | grep 'Figure of Merit'`
    elif [ "${app_dir}" == "kripke" ] ; then
      ok=`tail -n 2 $rf | head -n 1 | grep "END"`
    elif [ "${app_dir}" == "laghos" ] ; then
      ok=`tail -n 2 $rf | head -n 1 | grep 'Energy'`
    elif [ "${app_dir}" == "miniFE" ] ; then
      ok=`tail -n 2 $rf | head -n 1 | grep 'Final Resid Norm'`
    elif [ "${app_dir}" == "miniVite" ] ; then
      ok=`tail -n 3 $rf | head -n 1 | grep 'MODS'`
    elif [ "${app_dir}" == "SWFFT" ] ; then
      ok=`tail -n 3 $rf | head -n 1 | grep 'imag'`
    elif [ "${app_dir}" == "XSBench" ] ; then
      ok=`tail -n 3 $rf | head -n 1 | grep 'Verification'`
    else
      ok=0
    fi

    if [ "${duration}" == "" ] || [ "${ok}" == "" ] ; then
      echo arg_${a} run ${r} incomplete: $duration
      duration=""
      break
    else
      echo "arg_${a}/${r} ok"
    fi
  done
  popd 2> /dev/null > /dev/null
done
