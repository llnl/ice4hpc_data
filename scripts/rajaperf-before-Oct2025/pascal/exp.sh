#!/bin/sh

rep=0.5
sz=2.0
prob=rep${rep}-sz${sz}

RAJAPerf=/p/lustre2/yeom2/RAJAPerf-yeom2/install_toss4-nvcc11.8.0-60-gcc10.3.1-magic-pascal
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'

odir=${prob}
mkdir -p ${odir}
echo "${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
chmod u+x ${odir}/commands.sh
