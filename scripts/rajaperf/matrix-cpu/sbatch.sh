#!/bin/bash
#SBATCH --exclusive
#SBATCH -N 31
#SBATCH -p pbatch
#SBATCH -t 200

#SBATCH -A fractale

module load gcc/13.3.1-magic


num_smt_cores=224
num_threads=${num_smt_cores}
half=`echo ${num_threads} / 2 | bc`
qtr=`echo ${half} / 2 | bc`

rep=0.5


for sz in 0.5 1.0 2.0
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
