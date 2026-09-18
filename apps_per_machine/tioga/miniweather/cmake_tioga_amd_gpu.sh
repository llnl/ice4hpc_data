#!/bin/bash

source ${MODULESHOME}/init/bash
module reset
module load PrgEnv-amd cray-parallel-netcdf craype-accel-amd-gfx90a rocm/6.4.0

export TEST_MPI_COMMAND=""
unset MPICH_GPU_SUPPORT_ENABLED

./cmake_clean.sh

cmake -DCMAKE_CXX_COMPILER=CC                       \
      -DCMAKE_C_COMPILER=cc                         \
      -DCMAKE_Fortran_COMPILER=ftn                  \
      -DYAKL_ARCH="HIP"                             \
      -DYAKL_HIP_FLAGS="-DNO_INFORM -Ofast -ffast-math -D__HIP_ROCclr__ -D__HIP_ARCH_GFX90A__=1 --rocm-path=${ROCM_PATH} --offload-arch=gfx90a -x hip -Wno-unused-result" \
      -DLDFLAGS="--rocm-path=${ROCM_PATH} -L${ROCM_PATH}/lib -lamdhip64"                                  \
      -DNX=2048                                     \
      -DNZ=1024                                     \
      -DDATA_SPEC="DATA_SPEC_THERMAL"               \
      -DSIM_TIME=100                                \
      -DOUT_FREQ=-1                                 \
      -DYAKL_HAVE_MPI=ON                            \
      ..
