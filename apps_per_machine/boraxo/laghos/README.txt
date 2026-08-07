https://hypre.readthedocs.io/en/latest/ch-misc.html#building-the-library

=============================
Build dependencies first
============================
module load cmake/3.30.5 gcc/13.3.1-magic mvapich2/2.3.7

export PREFIX=/p/lustre1/yeom2/apps/install-boraxo

-------------
Umpire:
-------------
git clone https://github.com/LLNL/Umpire.git
(commit id b038daae Thu Oct 9 16:27:12 2025)
cd Umpire
git submodule update --init

cmake -S . -B build \
  -DUMPIRE_ENABLE_C=ON \
  -DUMPIRE_ENABLE_TOOLS=OFF \
  -DENABLE_BENCHMARKS=OFF \
  -DENABLE_EXAMPLES=OFF \
  -DENABLE_DOCS=OFF \
  -DENABLE_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_FLAGS="-g" \
  -DCMAKE_INSTALL_LIBDIR=${PREFIX}/lib \
  -DCMAKE_INSTALL_PREFIX=${PREFIX}

cmake --build build -j
cmake --install build
export umpire_DIR=${PREFIX}
export UMPIRE_DIR=${PREFIX}

-------------
Hypre:
-------------

git clone git@github.com:hypre-space/hypre.git
(commit id 26d08c2cd Wed Oct 8 19:38:51 2025)
cd hypre/build
cmake \
-DCMAKE_INSTALL_PREFIX=${PREFIX} \
-DCMAKE_BUILD_TYPE=Release \
-DHYPRE_ENABLE_MPI=ON \
-DHYPRE_ENABLE_OPENMP=ON \
-DHYPRE_WITH_EXTRA_CFLAGS="-g" \
-DHYPRE_WITH_EXTRA_CXXFLAGS="-g" \
../src

make -j
make install

-------------
METIS:
-------------
git clone https://github.com/mfem/tpls
cd tpls
tar zxvf metis-5.1.0.tar.gz
mv metis-5.1.0 ..
cd ../metis-5.1.0
edit Makefile to set prefix in line 7 to ${PREFIX}
edit set(GKlib_COPTS "-O3") at line 23 of GKlib/GKlibSystem.cmake to add '-g'
make PREFIX=${PREFIX} config
make OPTFLAGS="-Wno-error=implicit-function-declaration" -j
make install

-------------
MFEM:
-------------

git clone https://github.com/mfem/mfem
(commit id bf1b25d82e Tue Oct 7 13:22:38 2025)
cd mfem
mkdir build
cd build
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PREFIX}/lib:${PREFIX}/lib64 cmake \
  -DCMAKE_INSTALL_PREFIX=${PREFIX} \
  -DMFEM_USE_OPENMP:BOOL=ON \
  -DMFEM_USE_MPI:BOOL=ON \
  -DMFEM_USE_UMPIRE:BOOL=ON \
  -DCMAKE_CXX_FLAGS="-g" \
  ..

make -j
make install

===================
Laghos
===================

git clone https://github.com/CEED/Laghos.git
(commit id a2ad322 Fri May 9 17:31:45 2025)
cd Laghos

dos2unix laghos.cpp
#iconv -f utf-8 -f ascii//TRANSLIT laghos.cpp -o tmp.cpp && mv tmp.cpp laghos.cpp
LC_ALL=C tr -cd '\0-\177' < laghos.cpp > tmp.cpp && mv tmp.cpp laghos.cpp

sed -E 's/\$<\$<[^>]+>:[^:>]+:([^>]+)>/\1/g' ${PREFIX}/share/mfem/config.mk | sed 's/ dl / -ldl /g' > mfem_config.mk
sed -E 's/\$<\$<[^>]+>:[^:>]+:([^>]+)>/\1/g' ${PREFIX}/share/mfem/test.mk | sed 's/ dl / -ldl /g' > mfem_test.mk
cp mfem_*.mk serial

In the makefile under base directory and under serial directory,
Set INSTALL and MFEM_DIR to the value of ${PREFIX}
Set CONFIG_MK to mfem_config.mk at line 73
Set TEST_MK to mfem_test.mk at line 73

make -j

Copy the last command that results in a linking error and replace 'dl' with '-ldl'.
