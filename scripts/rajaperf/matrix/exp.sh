#!/bin/sh

base=ice4hpc_data/bins_per_machine
RAJAPerfSuite=${base}/matrix/rajaperf/raja-perf.exe

rep=0.5

for sz in 0.5 1.0 2.0
do
  prob=rep${rep}-sz${sz}
  odir=${prob}

  mkdir -p ${odir}
  echo "${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
  chmod u+x ${odir}/commands.sh
done
