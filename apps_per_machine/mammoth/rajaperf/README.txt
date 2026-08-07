Build:
  git clone git@github.com:LLNL/RAJAPerf.git --recursive
  (commit id 572956ab Mon Oct 6 15:21:34 2025)
  cd RAJAPerf
  module load gcc/13.3.1-magic
  scripts/lc-builds/toss4_gcc.sh 13.3.1
  cd build_lc_toss4-gcc-13.3.1
  make -j 16
  #vi cmake_install.cmake
  make install
  
