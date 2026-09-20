git clone --recurse-submodules git@github.com:mrnorman/miniWeather.git
(commit id b001069 Mon Aug 11 09:36:15 2025, YAKL submodule 71a059c)

Build (YAKL CUDA backend, executable: parallelfor):
  module load gcc/12.1.1-magic mvapich2/2.3.7 parallel-netcdf/1.12.3 cuda/12.2.2
  cd miniWeather/cpp/build
  copy cmake_lc_gnu_gpu.sh to the build dir
  ./cmake_lc_gnu_gpu.sh
  make -j 16 parallelfor

Run:
  module load gcc/12.1.1-magic mvapich2/2.3.7 parallel-netcdf/1.12.3 cuda/12.2.2
  ./parallelfor



================
 CPU only build
================

 Choose the compiler modules
-----------------------------

For corona-cpu, dane, mammoth, matrix-cpu:
module load gcc/13.3.1-magic mvapich2/2.3.7 parallel-netcdf/1.12.3 cmake/3.30.5

Current parallel-netcdf installation depends on mvapich

 Build
--------------------------

edit cmake_matrix-cpu.sh to enable/disable(comment out) ARC='-DYAKL_ARCH=OPENMP'

cp cmake_matrix-cpu.sh miniWeather/cpp/build
cp SetupPnetCDF.cmake miniWeather/cpp

cd miniWeather/cpp/build
source cmake_matrix-cpu.sh
make -j

