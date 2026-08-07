#!/bin/sh

rep=0.5
sz=0.5
num_smt_cores=192
max_core_id=`echo ${num_smt_cores} - 1 | bc`
max_cache_ways=16
max_num_cos=8
prob=rep${rep}-sz${sz}

pqos_dir=/opt/intel-cmt-cat
pqos="LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${pqos_dir}/lib ${pqos_dir}/bin/pqos"

RAJAPerf='/home/ec2-user/RAJAPerf/install_redhat-gcc-10'
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'

set_cos_1 ()
{
  echo ${pqos} -R
  echo ${pqos} -e '"llc:1=0x7fff"' #15
  echo ${pqos} -e '"llc:2=0x3fff"' #14
  echo ${pqos} -e '"llc:3=0x1fff"' #13
  echo ${pqos} -e '"llc:4=0x0fff"' #12
  echo ${pqos} -e '"llc:5=0x07ff"' #11
  echo ${pqos} -e '"llc:6=0x03ff"' #10
  echo ${pqos} -e '"llc:7=0x01ff"' #9
  echo ${pqos} -e '"llc:8=0x00ff"' #8
  echo ${pqos} -e '"llc:9=0x007f"' #7
  echo ${pqos} -e '"llc:10=0x003f"' #6
  echo ${pqos} -e '"llc:11=0x001f"' #5
  echo ${pqos} -e '"llc:12=0x000f"' #4
  echo ${pqos} -e '"llc:13=0x0007"' #3
  echo ${pqos} -e '"llc:14=0x0003"' #2
  echo ${pqos} -e '"llc:15=0x0001"' #1
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

