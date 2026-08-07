#!/bin/bash
#BSUB -nnodes 1
#BSUB -q pbatch
#BSUB -W 60

## ice4hpc bank for ruby, boraxo, lassen, mammoth, and corona.
#BSUB -G ice4hpc

module load cuda/12.0.0 gcc/8.3.1

RAJAPerf=/p/gpfs1/yeom2/RAJAPerf-yeom2/install_lc_blueos-nvcc12.0.0-70-gcc8.3.1
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'
rep=0.5

for sz in 0.5 1.0 2.0
do
    odir=rep${rep}-sz${sz}
    if [ ! -d ${odir} ] ; then
        continue
    fi

    pushd ${odir} 2> /dev/null > /dev/null
    echo ${odir}
    ./commands.sh
    popd 2> /dev/null > /dev/null
done
