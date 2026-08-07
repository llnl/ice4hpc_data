Build:
  git clone git@github.com:LLNL/Kripke.git
  (commit id 8cf3843 Sat Jul 5 16:48:51 2025)
  module load gcc/13.3.1-magic mvapich2/2.3.7
  cmake -DENABLE_MPI=ON -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g" ..
  make -j 16

Run:
  module load gcc/13.3.1-magic mvapich2/2.3.7
  ./kripke.exe
