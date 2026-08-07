git clone https://github.com/ANL-CESAR/XSBench
(commit id ba08e52 Mon Mar 11 14:09:13 2024)
cd XSBench

module load gcc/13.3.1-magic mvapich2/2.3.7 cmake/3.30.5
export PATH=${PATH}:/opt/rocm-6.4.2/bin
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/rocm-6.4.2/lib
export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:/opt/rocm-6.4.2:${PREFIX}
export ROCM_PATH=/opt/rocm-6.4.2

Build:
  
  XSBench is natively HIP-enabled. (No MPI)
  To build:
    cd hip
    edit Makefile to add '-g' to CFLAGS
    make -j

  XSBench-openmp-threading is CPU-only version with MPI and OpenMP support
  To build:
    cd openmp-threading
    make DEBUG=yes MPI=yes -j

  XSBench-openmp-offload is HIP-enabled via openmp-offload but with no MPI support
  To build:
    cd openmp-offload
    replace Makefile with Makefile-openmp-offload
    make CC=amdclang CXX=amdclang++ DEBUG=yes MPI=no -j

MPI is only supported for openmp-threading variants
