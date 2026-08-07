#!/bin/bash
#SBATCH -N 1
##SBATCH -p pbatch
#SBATCH -t 30

## ice4hpc bank for ruby, boraxo, lassen, mammoth, and corona.
#SBATCH -A ice4hpc

module load rocm/5.5.0

RAJAPerf=/p/lustre2/yeom2/RAJAPerf/install_lc_toss4-amdclang-5.5.0-gfx906
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
