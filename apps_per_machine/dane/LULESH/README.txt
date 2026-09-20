CPU only app: MPI and OpenMP are used

 Download source
-----------------
git@github.com:llnl/LULESH.git

git log shows the last commit as
commit 3e01c40b3281aadb7f996525cdd4a3354f6d3801



 Choose the compiler modules
-----------------------------

For corona-cpu, dane, mammoth, matrix-cpu:
module load gcc/13.3.1-magic cmake/3.30.5 openmpi/4.1.2

For tioga-cpu, tuolumne-cpu:
module load PrgEnv-gnu gcc/13.3.1-magic cray-mpich/9.0.1

For corona-cpu:
module load gcc/13.3.1-magic mvapich2/2.3.7


 Edit the Makefile
-------------------
In the Makefile, comment out `MPI_INC` and `MPI_LIB` and add the following
```
MPI_HOME := $(dir $(patsubst %/,%,$(dir $(shell which mpicc))))
MPI_INC = $(MPI_HOME)/include
MPI_LIB = $(MPI_HOME)/lib
```
