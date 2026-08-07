#!/bin/sh

rep=0.5
sz=1.0
num_smt_cores=72
max_core_id=`echo ${num_smt_cores} - 1 | bc`
max_cache_ways=11
max_num_cos=8
prob=rep${rep}-sz${sz}

pqos_dir=/opt/intel-cmt-cat
pqos="LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${pqos_dir}/lib ${pqos_dir}/bin/pqos"

RAJAPerf='/home/ec2-user/RAJAPerf/install_redhat-gcc-10'
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'

set_cos_1 ()
{
  echo ${pqos} -R
  echo ${pqos} -e '"llc:1=0x03ff"'
  echo ${pqos} -e '"llc:2=0x01ff"'
  echo ${pqos} -e '"llc:3=0x00ff"'
  echo ${pqos} -e '"llc:4=0x007f"'
  echo ${pqos} -e '"llc:5=0x003f"'
  echo ${pqos} -e '"llc:6=0x001f"'
  echo ${pqos} -e '"llc:7=0x000f"'
}

set_cos_2 ()
{
  echo ${pqos} -R
  echo ${pqos} -e '"llc:1=0x0007"'
  echo ${pqos} -e '"llc:2=0x0003"'
  echo ${pqos} -e '"llc:3=0x0001"'
}

vary_cache_ways_wo_SMT ()
{

  local n_th=$1
  local p_max=`echo ${max_cache_ways} - 1 | bc`
  local ff=`seq ${p_max} -1 1`
  local cos_id=1

  for f in $ff
  do
    local odir=cw${f}
    mkdir -p ${odir}

    if [ ${cos_id} -eq 1 ] ; then
      set_cos_1 > ${odir}/cos1.sh 
      chmod u+x ${odir}/cos1.sh
    elif [ ${cos_id} -eq ${max_num_cos} ] ; then
      cos_id=1
      set_cos_2 > ${odir}/cos2.sh
      chmod u+x ${odir}/cos2.sh
    fi

    echo "sudo ${pqos}"' -a "cos:'${cos_id}'=0-'${max_core_id}'"' > ${odir}/commands.sh
    echo "OMP_NUM_THREADS=${n_th} OMP_PLACES='{1}:${n_th}:2' OMP_PROC_BIND=true ${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" >> ${odir}/commands.sh
    chmod u+x ${odir}/commands.sh

    cos_id=`echo ${cos_id} + 1 | bc`
  done
}

half=`echo ${num_smt_cores} / 2 | bc`

for num_threads in ${half}
do
  odir=${prob}-${num_threads}
  mkdir -p ${odir}
  pushd ${odir} 2> /dev/null
  vary_cache_ways_wo_SMT ${half}
  popd 2> /dev/null
done

