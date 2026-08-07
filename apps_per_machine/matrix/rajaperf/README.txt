Build:
  module load cuda/12.9.1 gcc/13.3.1-magic
  git clone git@github.com:LLNL/RAJAPerf.git --recursive
  (commit id 572956ab Mon Oct 6 15:21:34 2025)
  cd RAJAPerf

  # to build a CPU only vesion modify run 'scripts/lc-builds/toss4_gcc.sh 13.3.1-magic'

  cp toss4_nvcc_gcc.sh scripts/lc-builds
  scripts/lc-builds/toss4_nvcc_gcc.sh 12.9.1 90 13.3.1-magic
  cd build_toss4-nvcc12.9.1-90-gcc-13.3.1-magic
  make -j 16
  #vi cmake_install.cmake
  make install
  
