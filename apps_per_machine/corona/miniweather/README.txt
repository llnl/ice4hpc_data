 Choose the compiler modules
-----------------------------

For corona-cpu, dane, mammoth, matrix-cpu:
module load gcc/13.3.1-magic mvapich2/2.3.7 parallel-netcdf/1.12.3 cmake/3.30.5

Current parallel-netcdf installation depends on mvapich

 Download source and build
--------------------------
https://github.com/mrnorman/miniWeather
commit: b001069e1f7654914744641013e2bd408a9206fb

edit cmake_dane.sh to enable/disable(comment out) ARC='-DYAKL_ARCH=OPENMP'

cp cmake_dane.sh miniWeather/cpp/build
cp SetupPnetCDF.cmake miniWeather/cpp

cd miniWeather
git submodule update --init --recursive
cd cpp/build
source cmake_dane.sh
make -j
