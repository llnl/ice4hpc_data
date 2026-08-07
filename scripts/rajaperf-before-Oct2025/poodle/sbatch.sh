#!/bin/bash
#SBATCH -N 1
#SBATCH -p pbatch
#SBATCH -t 180

## poodle and boraxo requires '--exclusive' sbatch option
## ice4hpc bank for ruby, boraxo, lassen, mammoth, and corona.
##SBATCH -A ice4hpc

module load gcc/10.3.1-magic

RAJAPerf=/p/lustre2/yeom2/RAJAPerf-yeom2/install_lc_toss4-gcc-10.3.1-magic-poodle
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'
num_smt_cores=224
rep=0.5

num_threads=${num_smt_cores}
half=`echo ${num_threads} / 2 | bc`
qtr=`echo ${half} / 2 | bc`

#for sz in 0.5 1.0 2.0
for sz in 2.0
do
    prob=rep${rep}-sz${sz}
    for n_th in ${num_threads} ${half} ${qtr} 32 16 8 4
    do
        odir=${prob}-${n_th}
        if [ ! -d ${odir} ] ; then
            continue
        fi

        pushd ${odir} 2> /dev/null > /dev/null
        echo ${odir}
        ./commands.sh
        popd 2> /dev/null > /dev/null
    done
done
