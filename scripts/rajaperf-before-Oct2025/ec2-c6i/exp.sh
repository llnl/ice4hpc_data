#!/bin/sh

rep=0.5
sz=2.0
num_smt_cores=64
prob=rep${rep}-sz${sz}

RAJAPerf='/home/ec2-user/RAJAPerf/install_redhat-gcc-10'
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'

num_threads=${num_smt_cores}
odir=${prob}-${num_threads}
mkdir -p ${odir}
echo "OMP_NUM_THREADS=${num_threads} OMP_PROC_BIND=true ${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
chmod u+x ${odir}/commands.sh


half=`echo ${num_threads} / 2 | bc`
qtr=`echo ${half} / 2 | bc`

for num_threads in ${half} ${qtr} 32 16 8 4
do
  odir=${prob}-${num_threads}
  mkdir -p ${odir}
  echo "OMP_NUM_THREADS=${num_threads} OMP_PLACES='{1}:${num_threads}:2' OMP_PROC_BIND=true ${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
  chmod u+x ${odir}/commands.sh
done

