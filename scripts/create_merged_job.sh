#!/bin/bash

# This script generates job scripts under a directory hierarchy as "machine/app/rank/args".
# There will be one job script per leaf directory, and it contains a single execution
# of a combination of machine, rank, app and args.

# The path to the base of the templates
base=ice4hpc_data/bins_per_machine

# The path to where a job script hierarchy is created under
exp_base=exp

# Job time limit
timeout=100

# The number of repeated execution of each combination of machine, rank, app and args.
repeats=`seq 1 3`

# In case of GPU enabled machines, the rank * num_nodes should match the number of GPUs.
# tuolumne, tioga and dane have 4 GPUs per node.
num_ranks="1 32"
max_ranks_per_node=32

# CPU time credit management bank.
bank=fractale

# Returns the number of nodes needed to run the given number of ranks
function get_num_nodes {
  local r=$1
  if [[ $((${r} - ${max_ranks_per_node})) -lt 0 ]] ; then
    echo 1
  else
    echo $(((${r} + ${max_ranks_per_node}-1)/${max_ranks_per_node}))
  fi
}


# The filename for stdout dump
outfile='out.txt'

# Enable/disable HPCToolkit measurement
#hpcrun_cmd='hpcrun'

machine=(
  borax
  boraxo
  corona
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
      if [ "${appvar}" == "" ] ; then
        appvar=${app_var[$(key ${app} ${m})]}
      fi
      exe="${base}/${mach[$m]}/${appdir}"/"${appexe}""${appvar}"
      if [ ! -x ${exe} ] ; then
        echo "${exe} does not exist!"
        continue
      fi

      app_arg_list=${base}/scripts/app_cmd/cmd_"${appexe}".${nranks}.txt
      if [ ! -f "${app_arg_list}" ] ; then
        echo "${app_arg_list} does not exist!"
        continue
      fi

      exp_path=${exp_base}/${mach[$m]}/${appdir}/nr${nranks}
      mkdir -p ${exp_path}
      if [ ! -d "${exp_path}" ] ; then
        continue
      fi
      pushd ${exp_path} 2> /dev/null

      ln -s ${base}/scripts/check_completion.sh 2> /dev/null
      echo 'for i in `seq 1 $1`; do pushd arg_$i; sbatch job.sh ; popd; done' > launch.sh
      chmod u+x launch.sh

      i_args=0
      while IFS= read -r args || [[ -n "$args" ]]; do
        args="`echo ${args} | cut -d' ' -f2-` ${arg_arch[$(key ${app} ${m})]}"

        mkdir -p arg_$((++ i_args))
        jobfile=arg_${i_args}/job.sh

        if [ ${app_gpu[${app}]} -eq 1 ] ; then
          app_gpu_opts=${gpu_opts[$m]}
        else
          app_gpu_opts=""
        fi
        launch_cmd=""

        echo '#!/bin/bash' > ${jobfile}

        if [ "${scheduler[$m]}" == "flux" ] ; then
          if [ "${bank}" != "" ] && [ ${m} != tioga ] ; then
            echo '#flux: --bank='${bank}  >>  ${jobfile}
          fi
          echo '#flux: -N '"${nn}" >>  ${jobfile}
          echo '#flux: -t'"${timeout}m" >>  ${jobfile}
          echo '#flux: --exclusive' >>  ${jobfile}
          echo '#flux: --job-name='"${appexe}:'${args}':${nranks}" >>  ${jobfile}
          echo '#flux: --output=stdout-{{id}}' >>  ${jobfile}
          echo '#flux: --error=stderr-{{id}}' >>  ${jobfile}
          if [ ${nranks} -gt 1 ] ; then
            launch_cmd="flux run --nodes=${nn} -n ${nranks} --exclusive -o mpibind=off -o cpu-affinity=per-task ${app_gpu_opts} "
          fi
        else
          if [ "${bank}" != "" ] ; then
            echo '#SBATCH --account='${bank}  >>  ${jobfile}
          fi
          echo '#SBATCH -N'"${nn}" >>  ${jobfile}
          echo '#SBATCH -t'"${timeout}" >>  ${jobfile}
          echo '#SBATCH --exclusive' >>  ${jobfile}
          echo '#SBATCH --job-name='"${appexe}:'${args}':${nranks}" >>  ${jobfile}
          echo '#SBATCH --output=stdout-%j' >>  ${jobfile}
          echo '#SBATCH --error=stderr-%j' >>  ${jobfile}
          if [ ${nranks} -gt 1 ] ; then
            launch_cmd="srun --nodes=${nn} -n ${nranks} --exclusive ${app_gpu_opts} "
          fi
          echo '' >>  ${jobfile}
        fi
        echo '' >>  ${jobfile}

        echo '' >>  ${jobfile}
        if [ "${hpcrun_cmd}" != "" ] ; then
          echo 'module load hpctoolkit/2024.01.1-python-3.10.8 python/3.10.8' >>  ${jobfile}
        fi
        echo 'source '${base}/scripts/utilities.bash >>  ${jobfile}
        echo '' >>  ${jobfile}
        if [ "${nthreads}" == "" ] ; then
          echo 'export OMP_NUM_THREADS=1' >>  ${jobfile}
        else
          echo 'export OMP_NUM_THREADS='${nthreads} >>  ${jobfile}
        fi
        echo "${env_arch[$(key ${app} ${m})]}" >>  ${jobfile}
        echo "${env_app[$(key ${app} ${m})]}" >>  ${jobfile}

        echo '' >>  ${jobfile}
        echo 'if [ "a" == "b" ] ; then' >>  ${jobfile}
        echo '  echo To skip this block. This block does not execute.' >>  ${jobfile}
        echo 'fi' >>  ${jobfile}
        echo '' >>  ${jobfile}

        for i_r in ${repeats}; do
          echo '' >>  ${jobfile}
          if [ "${scheduler[$m]}" == "flux" ] ; then
            echo 'ofile=`echo '${outfile}' | sed -e '"'"'s/\.txt/-'"'"'${FLUX_ENCLOSING_ID}'"'-${i_r}"'\.txt/'"'"'`' >>  ${jobfile}
          else
            echo 'ofile=`echo '${outfile}' | sed -e '"'"'s/\.txt/-'"'"'${SLURM_JOBID}'"'-${i_r}"'\.txt/'"'"'`' >>  ${jobfile}
          fi
          echo 'rm -f ${ofile}' >>  ${jobfile}

          echo '' >>  ${jobfile}

          if [ "${hpcrun_cmd}" != "" ] ; then
            i_evt=1
            for evt in "${hpcrun_events[@]}"; do
              #echo 'START=$(timestamp)' >>  ${jobfile}
              echo 'START=$(nanotimestamp)' >>  ${jobfile}
              echo "${launch_cmd}"'\' >>  ${jobfile}
              echo "     ${hpcrun_cmd} -o hpctoolkit-measurements-${i_r}-evt$((i_evt++)) ${evt}"'\' >>  ${jobfile}
              echo "     ${bash_time} ${exe} ${args} "'>> ${ofile}' >>  ${jobfile}
              echo 'END=$(nanotimestamp)' >>  ${jobfile}
              echo 'DURATION=$(diff_millisecs $START $END)' >>  ${jobfile}
              #echo 'END=$(timestamp)' >>  ${jobfile}
              #echo 'DURATION=$(diff_minutes $START $END)' >>  ${jobfile}
              echo 'echo DURATION ${DURATION} >> ${ofile}' >>  ${jobfile}
              echo '' >>  ${jobfile}
              echo 'sleep 1' >>  ${jobfile}
              echo '' >>  ${jobfile}
            done
          else #hpcrun_cmd
              #echo 'START=$(timestamp)' >>  ${jobfile}
              echo 'START=$(nanotimestamp)' >>  ${jobfile}
              echo "${launch_cmd}"'\' >>  ${jobfile}
              echo "     ${bash_time} ${exe} ${args} "'>> ${ofile}' >>  ${jobfile}
              echo 'END=$(nanotimestamp)' >>  ${jobfile}
              echo 'DURATION=$(diff_millisecs $START $END)' >>  ${jobfile}
              #echo 'END=$(timestamp)' >>  ${jobfile}
              #echo 'DURATION=$(diff_minutes $START $END)' >>  ${jobfile}
              echo 'echo DURATION ${DURATION} >> ${ofile}' >>  ${jobfile}
              echo '' >>  ${jobfile}
              echo 'sleep 1' >>  ${jobfile}
              echo '' >>  ${jobfile}
          fi # hpcrun_cmd
        done
      done < ${app_arg_list}

      popd 2> /dev/null
    done # nranks
  done # application
done # machine
