#!/bin/bash

# This scripts gathers DURATION in each stdout of all the runs
# (all the argument choices) of specific app and rank when
# executed under "machine/app/n_ranks".
# If there are repeated runs, only the median duration will be
# reported.
# Another script 'get_all_data.sh' traverses the directory hierarchy
# and gathers all the numbers relying on this script.

# beginning and end of application arguments
a_1=1
a_n=186

# beginning and end of repeated runs to read
r_1=1
r_n=3

if [ $# -eq 1 ] ; then
  a_n=$1
fi

ranks=`pwd | rev | cut -d '/' -f 1 | sed -e 's/rn$//' | rev`
app_dir=`pwd | rev | cut -d '/' -f 2 | rev`
machine=`pwd | rev | cut -d '/' -f 3 | rev`

for a in `seq ${a_1} ${a_n}`
do
  if [ ! -d arg_${a} ] ; then
    #echo "no more run for arg_${a}"
    break
  fi
  pushd arg_${a} 2> /dev/null > /dev/null

  args=`grep ${app_dir} job.sh | grep -v job-name | \
        tail -n 1 | \
        sed 's/^[[:space:]]*//' | \
        cut -d ' ' -f2- | rev | \
        cut -d '>' -f3- | rev | \
        sed 's/[[:space:]]*$//'`

  all_durations=$(
    t_cnt=0
    for r in `seq ${r_1} ${r_n}`
    do
      fcnt=`ls -1 out-*-${r}.txt 2> /dev/null | wc -l`
      if [ ${fcnt} -eq 0 ] ; then
        #echo arg_${a} run ${r} not run
        break
      elif [ ${fcnt} -gt 1 ] ; then
        #echo redundant output files in `pwd`:
        ls -1 out-*-${r}.txt
  
        mkdir -p old
        counter=1
        while [ ${counter} -lt ${fcnt} ] ; do
          ((counter++))
          rf_1=`ls -1 out-*-${r}.txt | head -n 1`
          mv ${rf_1} old
        done
      fi

      rf=`ls -1 out-*-${r}.txt | tail -n 1`
      duration="${duration} `tail -n 1 $rf | grep DURATION | awk '{print $2}'`"
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
        ok=""
        break
      fi

      if [ "${duration}" == "" ] || [ "${ok}" == "" ] ; then
        #echo arg_${a} run ${r} incomplete: $duration
        duration=""
        break
      fi
      ((t_cnt++))
    done
    echo ${t_cnt} ${duration}
  )
  cnt=`echo ${all_durations} | cut -d ' ' -f 1`

  echo ${all_durations} | cut -d ' ' -f2- | \
  awk -v cnt=${cnt} -v app_dir=${app_dir} -v machine=${machine} -v ranks=${ranks} -v args="${args}" \
  '{
     for (i = 1; i <= NF; i++) {
       a[i] = $i
     }

     # Sort the array 'a' numerically
     asort(a)

     # Calculate the median
     if (NF % 2 == 1) {
       # Odd number of elements: median is the middle element
       median = a[int((NF + 1) / 2)]
     } else {
       # Even number of elements: median is the average of the two middle elements
       median = (a[NF / 2] + a[(NF / 2) + 1]) / 2
     }

     if (cnt > 0) {
       printf("%s, %s, %s, %s, %f\n", app_dir, machine, ranks, args, median/1000.0)
     }
   }'

  popd 2> /dev/null > /dev/null
done
