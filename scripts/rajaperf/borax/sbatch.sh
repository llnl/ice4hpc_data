#!/bin/bash
#SBATCH --exclusive
#SBATCH -N 1
#SBATCH -p pbatch
#SBATCH -t 180

#SBATCH -A fractale

module load gcc/13.3.1-magic

num_smt_cores=72
num_threads=${num_smt_cores}

rep=0.5


for sz in 0.5 1.0 2.0
do
    prob=rep${rep}-sz${sz}
    for n_th in ${num_threads} 32 16 8 4
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
