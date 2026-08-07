GPU-enabled

git clone git@github.com:LLNL/Kripke.git
(commit id 8cf3843 Sat Jul 5 16:48:51 2025)

Build:
  module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic
  cd Kripke; mkdir build; cd build
  copy llnl-toss4-MI300A-rocm6.4.2-adams.cmake to the build directory
  cmake -DENABLE_MPI=ON -DENABLE_HIP=ON -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g" -C llnl-toss4-MI300A-rocm6.4.2-adams.cmake ..
  make -j 16

Run:
  module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic
  export HSA_XNACK=1
  export MPICH_GPU_SUPPORT_ENABLED=1
  ./kripke.exe
  flux run -n 1 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe
  flux run -n 4 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe --procs 1,2,2
  flux run -n 4 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe --procs 1,2,4 
