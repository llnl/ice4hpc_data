#!/bin/bash
# LLNL LC node: gcc 12 + CUDA 12.2 (H100, sm_90), YAKL CUDA backend.
# The code's file I/O uses parallel-netcdf, which needs an MPI library to link,
# so mvapich2 is loaded for linking only. Run the executables directly as a
# single process (no mpirun/srun needed).

source ${MODULESHOME}/init/bash
module load gcc/12.1.1-magic mvapich2/2.3.7 parallel-netcdf/1.12.3 cuda/12.2.2

# Strip stale PMI vars inherited from an enclosing srun step; mvapich2 singleton init crashes otherwise.
export TEST_MPI_COMMAND="env -u PMI_FD -u PMI_RANK -u PMI_SIZE -u PMI_JOBID"

PNETCDF_DIR=/usr/tce/packages/parallel-netcdf/parallel-netcdf-1.12.3-mvapich2-2.3.7-gcc-12.1.1

unset CUDAFLAGS
unset CXXFLAGS

./cmake_clean.sh

cmake -DCMAKE_CXX_COMPILER=mpicxx                    \
      -DCMAKE_C_COMPILER=mpicc                       \
      -DYAKL_ARCH="CUDA"                             \
      -DYAKL_CUDA_FLAGS="-O3 --use_fast_math -arch sm_90 -ccbin mpicxx -I${PNETCDF_DIR}/include" \
      -DLDFLAGS="-L${PNETCDF_DIR}/lib -lpnetcdf -Wl,-rpath,${PNETCDF_DIR}/lib" \
      -DCXXFLAGS="-O3 -I${PNETCDF_DIR}/include"      \
      -DNX=200                                       \
      -DNZ=100                                       \
      -DSIM_TIME=1000                                \
      -DOUT_FREQ=10                                  \
      ..
