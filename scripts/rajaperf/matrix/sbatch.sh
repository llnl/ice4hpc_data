#!/bin/bash
#SBATCH --exclusive
#SBATCH -N 1
#SBATCH -p pbatch
#SBATCH -t 100

#SBATCH -A fractale

module load cuda/12.9.1 gcc/13.3.1-magic


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
