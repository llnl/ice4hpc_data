#!/bin/sh

base=ice4hpc_data/bins_per_machine
RAJAPerfSuite=${base}/tioga/rajaperf/raja-perf.exe
repeats=`seq 1 3`

rep=0.5

for sz in 0.5 1.0 2.0
do
  prob=rep${rep}-sz${sz}
  odir=${prob}

  mkdir -p ${odir}

  echo "for i_r in ${repeats}; do" > ${odir}/commands.sh
  echo "  ${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz} >> results.txt" > ${odir}/commands.sh
  echo "done" > ${odir}/commands.sh

  chmod u+x ${odir}/commands.sh
done
