#!/bin/bash

# Gathers the results of kernels run in basic sequential mode
# on CPU-only machines and put them into a file per sizefact used.
#
# Transpose the Base_Seq of 'filtered.txt' such that the first
# row is the list of kernels, and the following rows are the
# timing numbers collected by Base_Seq.
# 'filtered.txt' is created by running 'filter.sh'


machines="borax boraxo corona-cpu dane mammoth"
machines="${machines} matrix-cpu tioga-cpu tuolumne-cpu"

# RAJAPef '--repfact' argument used
rep=0.5

# RAJAPef '--sizefact' argument used
sz="0.5 1.0 2.0"

# For repeated number of experiments
repeats=`seq 1 3`

print_header=1

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

      ff=`ls -1d rep${rep}-sz${s}-* 2> /dev/null`
      for f in ${ff}
      do
        pushd ${f} 2> /dev/null > /dev/null

        if [ ! -f 'filtered.txt' ] ; then
          echo "${m}/${i_m}/${f}/filtered.txt does not exist." > /dev/stderr
          continue
        fi

        # We pick the second column labelled as Base_Seq/default
        # Transpose the column(s)
        if [ ${print_header} -eq 1 ] ; then
          # The first column that contains kernel names as well as the column of interest
          awk -v m=${m} 'BEGIN{FS="[[:space:]]*,[[:space:]]*"; OFS=","} \
            (NR==1) { for (i=1; i<=NF; i++) { if ($i ~ /Base_Seq/) { col = i; break; } } }
            (NR==2) { for (i=col; i<=NF; i++) { if ($i ~ /default/) { col = i; break; } } }
            {h = h","$1; s = s","$col;} \
            END {h = "machine"h; s = m s; printf("%s\n%s\n", h, s)}' filtered.txt
          # We only need the kernel names once
          print_header=0
        else
          awk -v m=${m} 'BEGIN{FS="[[:space:]]*,[[:space:]]*"; OFS=","} \
            (NR==1) { for (i=1; i<=NF; i++) { if ($i ~ /Base_Seq/) { col = i; break } } }
            (NR==2) { for (i=col; i<=NF; i++) { if ($i ~ /default/) { col = i; break; } } }
            {s = s","$col;} \
            END {s = m s; printf("%s\n", s)}' filtered.txt
        fi

        popd 2> /dev/null > /dev/null
      done
      popd 2> /dev/null > /dev/null
    done
  done | ./avg.awk > "seq-c-rep${rep}-sz${s}".txt
done
