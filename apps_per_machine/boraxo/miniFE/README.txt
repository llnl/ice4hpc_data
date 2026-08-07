module load gcc/13.3.1-magic mvapich2/2.3.7 

git clone git@github.com:Mantevo/miniFE.git
(commit id abe3288 Mon Jul 17 12:43:29 2023)
cd miniFE
edit openmp/src/Makefile to add '-g' to CFLAGS
edit openmp-opt/src/Makefile to add '-g' to CFLAGS
cd ref/src; make
cd ../openmp/src; make
cd ../openmp-opt/src; make
