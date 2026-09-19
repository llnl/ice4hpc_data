git clone --recurse-submodules git@github.com:mrnorman/miniWeather.git
(commit id b001069 Mon Aug 11 09:36:15 2025, YAKL submodule 71a059c)

Build (YAKL HIP backend, executable: parallelfor):
  module reset
  module load PrgEnv-amd cray-parallel-netcdf craype-accel-amd-gfx942 rocm/6.4.0
  cd miniWeather/cpp/build
  copy cmake_tuolumne_amd_gpu.sh to the build dir
  ./cmake_tuolumne_amd_gpu.sh
  make -j 16 parallelfor

Run:
  module load PrgEnv-amd cray-parallel-netcdf craype-accel-amd-gfx942 rocm/6.4.0
  flux run -n 1 -N 1 --gpus-per-task=1 --exclusive ./parallelfor

----------------
 CPU only build
---------------

 Choose the compiler modules
-----------------------------

For tioga-cpu and tuolumne-cpu:
module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic cray-mpich/9.0.1 cray-parallel-netcdf/1.12.3.19


 Download source and build
--------------------------

edit cmake_tuolumne-cpu.sh to enable/disable(comment out) ARC='-DYAKL_ARCH=OPENMP'

cp cmake_tuolumne-cpu.sh miniWeather/cpp/build
cp SetupPnetCDF.cmake miniWeather/cpp

cd miniWeather/cpp/build
source cmake_tuolumne-cpu.sh
make -j
