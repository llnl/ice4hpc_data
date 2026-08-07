No GPU, CPU only

mpi and openmp

module load gcc/13.3.1-magic mvapich2/2.3.7
git clone git@github.com:ECP-ExaGraph/miniVite.git
(commit id 4cbf5be Wed Nov 13 19:07:42 2024)
cd miniVite
edit Makefile to replace CXX with mpic++
make -j
