#!/bin/bash

# This script traverses the experimental directory hierarchy,
# and gathers all the numbers using `get_all_data.sh'

base=ice4hpc_data/bins_per_machine
exp_base=exp
repeats=`seq 1 3`
# In case of GPU enabled machines, the rank * num_nodes should match the number of GPUs.
# tuolumne, tioga and dane have 4 GPUs per node.
num_ranks="1 32"
max_ranks_per_node=32

function get_num_nodes {
  local r=$1
  if [[ $((${r} - ${max_ranks_per_node})) -lt 0 ]] ; then
    echo 1
  else
    echo $(((${r} + ${max_ranks_per_node}-1)/${max_ranks_per_node}))
  fi
}


outfile='out.txt'
#hpcrun_cmd='hpcrun'

machine=(
  dane
  mammoth
  matrix
  tioga
  tuolumne
)

application=(
  amg
#  CoMD
  kripke
  laghos
  miniFE.x
  miniVite
  TestDfft
  XSBench
)

# Include various mapping definitions
if [ "${base}" == "" ] ; then
  script_path=$(realpath "$0")
  script_base_dir=$(dirname "${script_path}")
  . ${script_base_dir}/maps.sh
else
  . ${base}/scripts/maps.sh
fi


for m in "${machine[@]}"; do
  for app in "${application[@]}"; do
    for nranks in ${num_ranks[@]}; do
      nn=$(get_num_nodes ${nranks})
      appdir=${app_dir[$app]}
      appexe=${app_exe[$app]}
      appvar=${app_var[$app]}
      #exe="${base}/${mach[$m]}/${appdir}"/"${appexe}""${appvar}"
      #if [ ! -x ${exe} ] ; then
      #  echo "${exe} does not exist!"
      #  continue
      #fi

      exp_path=${exp_base}/${mach[$m]}/${appdir}/nr${nranks}
      if [ ! -d "${exp_path}" ] ; then
        continue
      fi

      pushd ${exp_path} 2> /dev/null > /dev/null
      ${base}/scripts/get_data.sh
      popd 2> /dev/null > /dev/null
    done # nranks
  done # application
done # machine
