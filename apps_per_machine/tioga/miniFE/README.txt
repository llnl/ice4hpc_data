git clone git@github.com:Mantevo/miniFE.git
(commit id abe3288 Mon Jul 17 12:43:29 2023)
module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic cray-mpich/9.0.1

MPI is turned on for all

cd miniFE

edit all Makefiles to add '-g' to CFLAGS and CXXFLAGS
cd ../ref/src; make
cd ../openmp/src; make
cd ../openmp-opt/src; make

openmp45 and openmp45-opt has been built using mpiamdclang
Use the updated Makefiles: Makefile-openmp45 and Makefile-openmp45-opt
For the latter, create the simlinks for basic, fem and utils directories
ln -s ../openmp45/basic basic
ln -s ../openmp45/fem fem
ln -s ../openmp45/utils utils
