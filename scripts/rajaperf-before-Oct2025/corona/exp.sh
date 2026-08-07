#!/bin/sh

rep=0.5
sz=2.0
prob=rep${rep}-sz${sz}

RAJAPerf=/p/lustre2/yeom2/RAJAPerf/install_lc_toss4-amdclang-5.5.0-gfx906
RAJAPerfSuite=${RAJAPerf}'/bin/raja-perf.exe'

odir=${prob}
mkdir -p ${odir}
echo "${RAJAPerfSuite} --repfact ${rep} --sizefact ${sz}" > ${odir}/commands.sh
chmod u+x ${odir}/commands.sh
