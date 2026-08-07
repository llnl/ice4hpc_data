#!/bin/bash

# Gathers the results of kernels run on GPUs and put them into
# a file per sizefact used.
#
# Transpose the Base_Seq of 'filtered.txt' such that the first
# row is the list of kernels, and the following rows are the
# timing numbers collected by Base_Seq.
# 'filtered.txt' is created by running 'filter.sh'


machines="corona matrix tioga tuolumne"

# RAJAPef '--repfact' argument used
rep=0.5

# RAJAPef '--sizefact' argument used
sz="0.5 1.0 2.0"

# For repeated number of experiments
repeats=`seq 1 3`

print_header=1

declare -A gpu_type
gpu_type["corona"]=Base_HIP
gpu_type["matrix"]=Base_CUDA
gpu_type["tioga"]=Base_HIP
gpu_type["tuolumne"]=Base_HIP

for s in ${sz}
do
  for m in ${machines}
  do
    for i_m in ${repeats}
    do
      if [ ! -d ${m}/${i_m} 2> /dev/null ] ; then
        echo "Directory ${m}/${i_m} does not exist!" > /dev/stderr
        continue
      fi
      pushd ${m}/${i_m} 2> /dev/null > /dev/null

      ff=`ls -1d rep${rep}-sz${s}* 2> /dev/null`

      for f in ${ff}
      do
        pushd ${f} 2> /dev/null > /dev/null

        if [ ! -f 'filtered.txt' ] ; then
          echo "${m}/${i_m}/${f}/filtered.txt does not exist." > /dev/stderr
          continue
        fi

        # Depending on the type of machine, RAJAPerf output may have diffferent number of columnes
        # We pick the column labelled as Base_CUDA or Base_HIP, the first variant of the kind.
        # Transpose the column(s)
        if [ ${print_header} -eq 1 ] ; then
          # The first column that contains kernel names as well as the column of interest
          awk -v m=${m} -v Type=${gpu_type[${m}]} \
            'BEGIN{FS="[[:space:]]*,[[:space:]]*"; OFS=","}
             (NR==1) { for (i=1; i<=NF; i++) { if ($i ~ Type) { col = i; break; } } }
             (NR==2) { for (i=col; i<=NF; i++) { if ($i ~ /block_256/) { col = i; break; } } }
             {h = h","$1; s = s","$col;}
             END {h = "machine"h; s = m s; printf("%s\n%s\n", h, s); }' filtered.txt
          # We only need the kernel names once
          print_header=0
        else
          awk -v m=${m} -v Type=${gpu_type[${m}]} \
            'BEGIN{FS="[[:space:]]*,[[:space:]]*"; OFS=","}
             (NR==1) { for (i=1; i<=NF; i++) { if ($i ~ Type) { col = i; break } } }
             (NR==2) { for (i=col; i<=NF; i++) { if ($i ~ /block_256/) { col = i; break; } } }
             {s = s","$col;}
             END {s = m s; printf("%s\n", s)}' filtered.txt
        fi

        popd 2> /dev/null > /dev/null
      done
      popd 2> /dev/null > /dev/null
    done
  done | ./avg.awk > "gpu-rep${rep}-sz${s}".txt
done
