export PATH=${PATH}:/opt/rocm-6.4.2/bin
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/rocm-6.4.2/lib
export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:/opt/rocm-6.4.2:${PREFIX}
export ROCM_PATH=/opt/rocm-6.4.2

Build:
  module load gcc/13.3.1-magic mvapich2/2.3.7 cmake/3.30.5
  git clone git@github.com:LLNL/RAJAPerf.git --recursive
  (commit id 572956ab Mon Oct 6 15:21:34 2025)
  cd RAJAPerf

  copy toss4_amdclang-corona.sh to scripts/lc-builds
  scripts/lc-builds/toss4_amdclang-corona.sh 6.4.2 gfx906
  cd build_lc_toss4-amdclang-6.4.2-gfx906
  make -j 16
  make install
  
