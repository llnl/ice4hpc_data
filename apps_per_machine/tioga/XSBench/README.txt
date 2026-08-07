git clone https://github.com/ANL-CESAR/XSBench
(commit id ba08e52 Mon Mar 11 14:09:13 2024)
cd XSBench

Build:
  module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic
  
  XSBench is natively HIP-enabled. (No MPI)
  To build:
    cd hip
    edit Makefile to add '-g' to CFLAGS
    make -j

  XSBench-openmp-threading is CPU-only version with MPI and OpenMP support
  To build:
    cd openmp-threading
    make DEBUG=yes MPI=yes -j

  XSBench-openmp-offload is HIP-enabled via openmp-offload with MPI support
  To build:
    cd openmp-offload
    replace Makefile with Makefile-openmp-offload
    make CC=mpiamdclang CXX=mpiamdclang++ DEBUG=yes MPI=yes -j

MPI is not supported for hip or cuda variants
