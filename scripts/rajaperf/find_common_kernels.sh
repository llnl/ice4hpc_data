#!/bin/bash
# This script finds the common set of kernels from the summary.txt 
# outputs with old RAJAPerf and the latest.

new_set=summary.txt
old_set=summary-old.txt

if [ ! -f "${new_set}" ] || [ ! -f "${old_set}" ] ; then
  echo "data files do not exist!"
  exit 1
fi

awk \
'BEGIN {
  #FS = ","
  FS = "[[:space:]]*,[[:space:]]*"
  OFS = ","
}
(FNR == 1){
  fcnt ++;
  # skipping 4 fields: machine, rep, sz, n_threads
  for (k=5; k <= NF; k++) {
    kernel_idx[fcnt" "$k] = k
    kernel_name[fcnt" "k] = $k
  }
  num_kernels[fcnt] = NF
  nextfile
}

END {
  for (k=1; k <= num_kernels[fcnt]; k++) {
    kn = kernel_name[fcnt" "k] 
    not_common = 0;
    for (i=1; i < fcnt; i++) {
      ki = kernel_idx[i" "kn];
      if (ki == 0) {
        not_common = 1;
        break
      }
    } 
    if (not_common == 0) {
      #printf(", %s", kn);
      printf("%s\n", kn);
    }
  }
#  printf("\n")
}' $new_set $old_set
