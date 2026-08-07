#!/bin/bash

# Create machine representation vector for each machine
# Pick up the set of values associated with RAJAPerf benchmarking kernels with
# each sizefact arg value. Then, concatenate those.
# If there are 62 kernels to be used and 3 sizefact choices, then a vector of
# total 186 values will be created for each machine

outfile=machine_rep.txt

# list of common kernels to pick, which is a result of `find_common_kernels.sh`
common_kernels_file=common_kernels.txt

# The name of the summary file
summary_file=summary.txt

# RAJAPef '--repfact' argument used
rep=0.5

# RAJAPef '--sizefact' argument used
sz="0.5 1.0 2.0"

# Machines to pick from summary_file, CPU-only and GPU
seq_c_machines="boraxo catalyst ec2-c5n ec2-c6a ec2-c6i mammoth poodle quartz ruby corona ec2-p3 ec2-p4d lassen pascal tioga"

# Machines to pick from seq-g-rep*-sz* files, i.e, CPUs of GPU-enabled machines
seq_g_machines="corona ec2-p3 ec2-p4d lassen pascal tioga"


if [ ! -f "${common_kernels_file}" 2> /dev/null ] ; then
  echo "${common_kernels_file} does not exist!" > /dev/stderr
  exit
fi

# Kernels to be used
kernels=`cat ${common_kernels_file}`

if [ ! -f "${summary_file}" 2> /dev/null ] ; then
  echo "${summary_file} does not exist!" > /dev/stderr
  exit
fi

for s in ${sz}
do
  df=seq-g-rep${rep}-sz${s}.txt
  if [ ! -f "${df}" 2> /dev/null ] ; then
    echo "${df} does not exist!" > /dev/stderr
    continue
  fi
  seq_g_files="${seq_g_files} ${df}"
done

echo "Extract the values of ${seq_c_machines} from ${summary_file}" > /dev/stderr

# Extract the values of seq_c_machines from summary_file
awk -v machines="${seq_c_machines}" -v sizes="${sz}" -v kernels="${kernels}" \
 'BEGIN {
    FS="[[:space:]]*,[[:space:]]*"; OFS=",";
    n_m = split(machines, machine, " ")
    n_sz = split(sizes, size, " ")
    n_k = split(kernels, kernel, " ")
  }
  (NR == 1) {
    nf = NF;
    # Record the field indices of kernels that are of interests
    i_k = 1
    for (i=1; i <= NF; i++) {
      if ($i == kernel[i_k]) {
        k_idx[i_k] = i;
        if (i_k == n_k) break;
        else i_k ++
      }
    }
    # Print the header, i.e., the names of kernels that are of interests
    printf("machine");
    for (j=1; j <= n_sz; j++) {
      for (i = 1; i <= n_k; i++) {
        idx = k_idx[i]
        printf("%s%s", OFS, $(idx));
      }
    }
    printf("\n")
  }
  #machine, rep, sz, n_threads,
  (NR>1) {
    if (($2 == "0.5") && ($4 == 1)) {
      sz = $3
      for (i = 1; i <= n_k; i++) {
        idx = k_idx[i]
        data[$1 " " sz " " idx] = $idx
      }
    }
  }
  END {
    for (k=1; k <= n_m ; k++) {
      m = machine[k];
      printf("%s", m);

      for (j=1; j <= n_sz; j++) {
        sz = size[j];
        for (i = 1; i <= n_k; i++) {
          idx = k_idx[i]
          printf("%s%s", OFS, data[m " " sz " " idx]);
        }
      }

      printf("\n");
    }
  }' ${summary_file} > ${outfile}

echo "Extract the values of ${seq_g_machines} from ${seq_g_files}" > /dev/stderr
# Extract the values of seq_g_machines from seq_g_files
awk -v sizes="${sz}" -v kernels="${kernels}" \
 'BEGIN {
    FS="[[:space:]]*,[[:space:]]*"; OFS=",";
    n_sz = split(sizes, size, " ")
    n_k = split(kernels, kernel, " ")
  }
  (NR == 1) {
    nf = NF;
    # Record the field indices of kernels that are of interests
    i_k = 1
    for (i=1; i <= NF; i++) {
      if ($i == kernel[i_k]) {
        k_idx[i_k] = i;
        if (i_k == n_k) break;
        else i_k ++
      }
    }
    # Print the header, i.e., the names of kernels that are of interests
    #printf("machine");
    #for (j=1; j <= n_sz; j++) {
    #  for (i = 1; i <= n_k; i++) {
    #    idx = k_idx[i]
    #    printf("%s%s", OFS, $(idx));
    #  }
    #}
    #printf("\n")
  }
  (FNR == 1) {
    read_on = 0; # reset read flag
    fcnt ++; # file count
  }
  {
    if ($1 ~ /AVERAGE/) {
      # Only read after "AVERAGE"
      read_on = 1; # set read flag on
      next
    }
    if (read_on == 0) {
      # Read only when read flag is on, i.e., after "AVERAGE"
      next
    }
    # Check if the machine name has been seen
    if (mach[$1] == 0) {
      n_mach ++;
      mach[$1] = n_mach; # Record the new machine name seen
    }
    for (i = 1; i <= n_k; i++) {
      idx = k_idx[i]
      data[$1 " " fcnt " " idx] = $idx
    }
  }
  END {
    for (m in mach) {
      printf("%s-cpu", m);
      for (j=1; j <= fcnt; j++) {
        for (i = 1; i <= n_k; i++) {
          idx = k_idx[i]
          printf("%s%s", OFS, data[m " " j " " idx]);
        }
      }
      printf("\n")
    }
  }'  ${seq_g_files} >> ${outfile}
