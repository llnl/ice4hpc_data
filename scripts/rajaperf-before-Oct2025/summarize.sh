#!/bin/bash

# Summarize the report files. i.e., Read all the per-machine average kernel
# times for various rajaperf.exe parameters

outfile=summary.txt

reports="seq-c gpu omp-c"

# RAJAPef '--repfact' argument used
rep=0.5

# RAJAPef '--sizefact' argument used
sz="0.5 1.0 2.0"

# For repeated number of experiments
repeats=`seq 1 3`

header_read=0


tmp_sorted=$(mktemp)
tmp_unsorted=$(mktemp)
trap 'rm -f "$tmp_sorted" "$tmp_unsorted"' EXIT


for rp in ${reports}
do
  if [[ "${rp}" =~  ^omp ]] ; then
    num_omp_threads=""
    odirect=${tmp_unsorted}
  else
    num_omp_threads=1
    odirect=${tmp_sorted}
  fi

  for s in ${sz}
  do
      rfile=${rp}-rep${rep}-sz${s}.txt
      if [ ! -f ${rfile} 2> /dev/null ] ; then
        echo "File ${rfile} does not exist!" > /dev/stderr
        continue
      fi

      if [ ${header_read} -eq 0 ] ; then
        header_read=1
        header=`head -n 1 ${rfile} | awk -v n_threads="${num_omp_threads}" \
        'BEGIN { FS="[[:space:]]*,[[:space:]]*"; OFS="," }
         {
           printf("%s, rep, sz", $1);
           if (n_threads != "") { # otherwise, it is already in the data
             printf(", n_threads");
             i = 4
           } else {
             printf(", %s", $2);
             i = 5
           }
           for (; i<=NF; ++i) {
             printf(", %s", $i);
           }
           printf("\n")
         }'`
      fi

      awk -v rep="${rep}" -v sz="${s}" -v n_threads="${num_omp_threads}" \
        'BEGIN { FS="[[:space:]]*,[[:space:]]*"; OFS="," }
         ($1 ~ /AVERAGE/){is_on=1; next}
         (is_on){
           printf("%s, %s, %s", $1, rep, sz);
           if (n_threads != "") { # otherwise, it is already in the data
             printf(", %s", n_threads);
             i = 4
           } else {
             printf(", %s", $2);
             i = 5
           }
           for (; i<=NF; ++i) {
             printf(", %s", $i);
           }
           printf("\n")
         }' ${rfile}
  done >> ${odirect}
done

echo ${header} > ${outfile}
cat ${tmp_sorted} | sort >> ${outfile}
cat ${tmp_unsorted} | awk 'BEGIN{FS="[[:space:]]*,[[:space:]]*"} (NF>3){print $0}' >> ${outfile}
