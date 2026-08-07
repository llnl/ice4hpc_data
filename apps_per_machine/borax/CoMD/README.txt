module load gcc/13.3.1-magic mvapich2/2.3.7 

CPU only

mpi and openmp

git clone https://github.com/ECP-copa/CoMD
cd CoMD/src-openmp
cp Makefile.vanilla Makefile
make
cd ../bin
