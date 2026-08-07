#
# Copyright (c) 2014-25, Lawrence Livermore National Security, LLC
# and Kripke project contributors. See the Kripke/COPYRIGHT file for details.
# 
# SPDX-License-Identifier: (BSD-3-Clause)
#

# module load rocmcc/5.6.0-cce-16.0.0a-magic
# module load rocm/5.6.0

set(RAJA_COMPILER "RAJA_COMPILER_CLANG" CACHE STRING "")

set(CMAKE_C_COMPILER   "mpicc" CACHE PATH "")
set(CMAKE_CXX_COMPILER "mpic++" CACHE PATH "")
set(ENABLE_MPI_WRAPPER OFF)
set(ENABLE_FIND_MPI ON CACHE BOOL "")

set(CMAKE_CXX_FLAGS "" CACHE STRING "")
set(CMAKE_CXX_FLAGS_RELEASE "-std=c++14 -O3 -ffast-math" CACHE STRING "")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-std=c++14 -O3 -g -ffast-math" CACHE STRING "")
set(CMAKE_CXX_FLAGS_DEBUG "-std=c++14 -O0 -g" CACHE STRING "")

set(ROCM_ROOT_DIR "/opt/rocm-6.4.2" CACHE PATH "")
set(HIP_ROOT_DIR "/opt/rocm-6.4.2/hip" CACHE PATH "")
set(HIP_PATH "/opt/rocm-6.4.2/llvm/bin" CACHE PATH "")
set(CMAKE_HIP_ARCHITECTURES "gfx906" CACHE STRING "")
set(GPU_TARGETS "gfx906" CACHE STRING "")
set(AMD_GPU_TARGETS "gfx906" CACHE STRING "")

set(ENABLE_CHAI On CACHE BOOL "")
set(ENABLE_HIP On CACHE BOOL "")
set(ENABLE_OPENMP Off CACHE BOOL "")
set(ENABLE_MPI On CACHE BOOL "")

#set(CMAKE_HIPCC_FLAGS_RELEASE "-O3 --expt-extended-lambda" CACHE STRING "")
#set(CMAKE_HIPCC_FLAGS_RELWITHDEBINFO "-O3 -lineinfo --expt-extended-lambda" CACHE STRING "")
#set(CMAKE_HIPCC_FLAGS_DEBUG "-O0 -g -G --expt-extended-lambda" CACHE STRING "")
#set(CMAKE_HIPCC_HOST_COMPILER "${CMAKE_CXX_COMPILER}" CACHE STRING "")

# For LLNL TCE packages
set(ENABLE_MPI_WRAPPER On CACHE BOOL "")


