git clone https://github.com/ANL-CESAR/XSBench
(commit id ba08e52 Mon Mar 11 14:09:13 2024)
cd XSBench

Build:
  module load gcc/13.3.1-magic cuda/12.9.1
  
  XSBench is CUDA-enabled via native cuda (No MPI)
  To build:
    cd cuda
    edit Makefile to set SM_VERSION = 90
    make DEBUG=yes -j

  XSBench-openmp-threading is CPU-only version with MPI and OpenMP support
  To build:
    cd openmp-threading
    make DEBUG=yes MPI=yes -j

  XSBench-openmp-offload is CUDA-enabled via openmp-offload with MPI support
  To build:
    cd openmp-offload
    module load clang/19.1.3-magic cuda/12.9.1
    - Replace Makefile with Makefile-openmp-offload
    - Replace '#ifdef MPI' with '#ifdef XSB_MPI' in the source files (e.g., Main.c and io.c).
      The reason is that MPI is used by a macro definition in MPICH header.
      So, the -DMPI in the makefile to enable `#ifdef MPI' blocks conflict with the MPI header.
      Same edits might need for 'ifndef' or '#if defined()'
    make CC=mpicc CXX=mpicxx DEBUG=yes MPI=yes -j

MPI is not supported for hip or cuda variants
