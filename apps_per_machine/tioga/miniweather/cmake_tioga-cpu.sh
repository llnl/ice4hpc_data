#!/bin/bash

module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic cray-mpich/9.0.1  cray-parallel-netcdf/1.12.3.19 cmake/3.29.2
export PARALLEL_NETCDF_ROOT=/opt/cray/pe/parallel-netcdf/1.12.3.19/cray/20.0

ARC='-DYAKL_ARCH=OPENMP'

export TEST_MPI_COMMAND="srun -n 1"
unset CUDAFLAGS
#unset CXXFLAGS

unset OMPI_CXX
unset OMPI_CC
unset OMPI_F90
unset OMPI_FC

./cmake_clean.sh

cmake -DCMAKE_CXX_COMPILER=mpic++         \
      -DCMAKE_C_COMPILER=mpicc            \
      -DCMAKE_Fortran_COMPILER=mpif90     \
      -DYAKL_CXX_FLAGS="-DSIMD_LEN=4 -Ofast -march=native -mtune=native -DNO_INFORM -I${PARALLEL_NETCDF_ROOT}/include"   \
      -DLDFLAGS="-L${PARALLEL_NETCDF_ROOT}/lib -lpnetcdf"  \
      -DCMAKE_PREFIX_PATH=${PARALLEL_NETCDF_ROOT} \
      -DPNETCDF_DIR=${PARALLEL_NETCDF_ROOT} \
      -DNX=256                            \
      -DNZ=128                            \
      -DSIM_TIME=250                      \
      -DOUT_FREQ=2000                     \
      ${ARC} ..

