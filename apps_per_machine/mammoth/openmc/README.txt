CPU only, OpenMP default, MPI optional

module load gcc/13.3.1-magic cmake/3.30.5 openmpi/4.1.2

https://docs.openmc.org/en/stable/quickinstall.html#manually-installing-from-source
commit: afa7a14ac5cb8630f642a77229ca64dc3eaeef81

git clone --recurse-submodules https://github.com/openmc-dev/openmc.git

mkdir openmp/build
cd openmp/build
cmake -DOPENMC_USE_MPI=ON -DOPENMC_USE_OPENMP=ON -DCMAKE_INSTALL_PREFIX=`realpath ../install` ..
make -j
make install
