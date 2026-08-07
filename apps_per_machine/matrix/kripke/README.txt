Build:
  git clone git@github.com:LLNL/Kripke.git
  (commit id 8cf3843 Sat Jul 5 16:48:51 2025)
  module load gcc/13.3.1-magic cuda/12.9.1
  cd Kripke; mkdir build; cd build
  copy llnl-toss4-H100-nvcc-gcc.cmake to the build dir
  cmake -DENABLE_MPI=ON -DENABLE_CUDA=ON -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g" -C llnl-toss4-H100-nvcc-gcc.cmake ..
  make -j 16

Run:
  module load gcc/13.3.1-magic cuda/12.9.1
  ./kripke.exe
