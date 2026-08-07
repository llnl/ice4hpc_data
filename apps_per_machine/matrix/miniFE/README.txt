git clone git@github.com:Mantevo/miniFE.git
(commit id abe3288 Mon Jul 17 12:43:29 2023)
module load cuda/12.9.1 gcc/13.3.1-magic mvapich2/2.3.7 

MPI is turned on for all

cd miniFE
cd cuda/src
edit Makefile and CudaELLMatrix.hpp
  add '-g' to CFLAGS and CXXFLAGS
make -j

edit all Makefiles to add '-g' to CFLAGS and CXXFLAGS
cd ../ref/src; make
cd ../openmp/src; make
cd ../openmp-opt/src; make

openmp45 and openmp45-opt has been built using clang/19.1.3-magic and mpi
Use the updated Makefiles: Makefile-openmp45 and Makefile-openmp45-opt
For the latter, create the simlinks for basic, fem and utils directories
ln -s ../openmp45/basic basic
ln -s ../openmp45/fem fem
ln -s ../openmp45/utils utils
