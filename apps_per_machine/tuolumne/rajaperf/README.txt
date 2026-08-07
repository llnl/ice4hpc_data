Build:
  module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic
  git clone git@github.com:LLNL/RAJAPerf.git --recursive
  (commit id 572956ab Mon Oct 6 15:21:34 2025)
  cd RAJAPerf

  # to build a CPU only vesion modify 'scripts/lc-builds/toss4_amdclang.sh' to set -DENABLE_HIP=OFF

  scripts/lc-builds/toss4_amdclang.sh 6.4.2 gfx942
  cd build_lc_toss4-amdclang-6.4.2-gfx942
  make -j 16
  make install
  
