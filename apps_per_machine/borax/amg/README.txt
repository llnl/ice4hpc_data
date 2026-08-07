No GPU, CPU only
mpi and openmp

module load gcc/13.3.1-magic mvapich2/2.3.7
git clone git@github.com:LLNL/AMG.git
(commit id 3ada8a1 Wed Nov 21 08:18:49 2018)

cd AMG
edit Makefile.include to add '-g' to INCLUDE_CFLAGS
edit test/Makefile to add '-g' to amg and .o targets

make -j
cd test
