#!/bin/sh

rep=0.5
sz=2.0
prob=rep${rep}-sz${sz}

RAJAPerf=/p/gpfs1/yeom2/RAJAPerf-yeom2/install_lc_blueos-nvcc12.0.0-70-gcc8.3.1
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'

odir=${prob}
mkdir -p ${odir}
echo "lrun -1 --smpiargs=-disable_gpu_hooks ${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
chmod u+x ${odir}/commands.sh
