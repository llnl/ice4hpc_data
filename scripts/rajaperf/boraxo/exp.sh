#!/bin/sh

base=ice4hpc_data/bins_per_machine
RAJAPerfSuite=${base}/boraxo/rajaperf/raja-perf.exe

num_smt_cores=72
num_threads=${num_smt_cores}

rep=0.5

for sz in 0.5 1.0 2.0
do
  prob=rep${rep}-sz${sz}
  
  odir=${prob}-${num_threads}
  mkdir -p ${odir}
  echo "OMP_NUM_THREADS=${num_threads} OMP_PROC_BIND=true ${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
  chmod u+x ${odir}/commands.sh
  
  
  for n_threads in 32 16 8 4
  do
    odir=${prob}-${n_threads}
    mkdir -p ${odir}
    echo "OMP_NUM_THREADS=${n_threads} OMP_PLACES='{1}:${n_threads}:2' OMP_PROC_BIND=true ${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
    chmod u+x ${odir}/commands.sh
  done
done
