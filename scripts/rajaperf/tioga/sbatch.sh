#!/bin/bash
#SBATCH --exclusive
#SBATCH -N 1
##SBATCH -p pbatch
#SBATCH -t 30

##SBATCH -A fractale

module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic


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
