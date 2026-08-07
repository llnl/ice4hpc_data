MPI+OpenMP

module load gcc/13.3.1-magic mvapich2/2.3.7

git clone https://github.com/ANL-CESAR/XSBench
(commit id ba08e52 Mon Mar 11 14:09:13 2024)
cd XSBench/openmp-threading
# compile with -g
make DEBUG=yes MPI=yes
