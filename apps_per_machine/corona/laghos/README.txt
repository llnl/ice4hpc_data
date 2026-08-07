https://hypre.readthedocs.io/en/latest/ch-misc.html#building-the-library

=============================
Build dependencies first
============================

module load clang/19.1.3-magic mvapich2/2.3.7 cmake/3.30.5


export PREFIX=/p/lustre1/yeom2/apps/install-corona
export PATH=${PATH}:/opt/rocm-6.4.2/bin
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/rocm-6.4.2/lib
export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}:/opt/rocm-6.4.2:${PREFIX}
export ROCM_PATH=/opt/rocm-6.4.2
export ENABLE_CUDA=OFF
export ENABLE_HIP=ON
export HIP_ARCH=gfx906


-------------
Umpire:
-------------
git clone https://github.com/LLNL/Umpire.git
(commit id b038daae Thu Oct 9 16:27:12 2025)
cd Umpire
git submodule update --init

# note that an extra option is added: GPU_TARGETS=
CC=`which amdclang` CXX=`which amdclang++` cmake -S . -B build \
  -DUMPIRE_ENABLE_C=ON \
  -DUMPIRE_ENABLE_TOOLS=OFF \
  -DENABLE_HIP=${ENABLE_HIP} \
  -DCMAKE_HIP_ARCHITECTURES=${HIP_ARCH} \
  -DGPU_TARGETS=${HIP_ARCH} \
  -DENABLE_BENCHMARKS=OFF \
  -DENABLE_EXAMPLES=OFF \
  -DENABLE_DOCS=OFF \
  -DENABLE_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_FLAGS="-g" \
  -DCMAKE_INSTALL_LIBDIR=${PREFIX}/lib \
  -DCMAKE_INSTALL_PREFIX=${PREFIX} \
  -DCMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}

cmake --build build -j
cmake --install build
export umpire_DIR=${PREFIX}
export UMPIRE_DIR=${PREFIX}

-------------
Hypre:
-------------

git clone git@github.com:hypre-space/hypre.git
(commit id 26d08c2cd Wed Oct 8 19:38:51 2025)
export ROCM_PATH=/opt/rocm-6.4.2
cd hypre/build

# note that an extra option is added: GPU_TARGETS=
CC=`which amdclang` CXX=`which amdclang++` cmake \
-DCMAKE_INSTALL_PREFIX=${PREFIX} \
-Dumpire_DIR=${PREFIX} \
-DCMAKE_BUILD_TYPE=Release \
-DHYPRE_ENABLE_MPI=ON \
-DHYPRE_ENABLE_UMPIRE=ON \
-DHYPRE_ENABLE_OPENMP=ON \
-DHYPRE_WITH_EXTRA_CFLAGS="-g" \
-DHYPRE_WITH_EXTRA_CXXFLAGS="-g" \
-DCMAKE_HIP_ARCHITECTURES=${HIP_ARCH} \
-DGPU_TARGETS=${HIP_ARCH} \
-DHYPRE_ENABLE_HIP=${ENABLE_HIP} \
-DCMAKE_PREFIX_PATH=/opt/rocm-6.4.2/lib/cmake \
-DMPI_INCLUDE_DIR=/usr/tce/packages/mvapich2/mvapich2-2.3.7-clang-19.1.3-magic/include \
../src

#-DMPI_INCLUDE_DIR=/usr/tce/packages/mvapich2/mvapich2-2.3.7-gcc-13.3.1-magic/include \

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

Note that there is a PR for mfem to fix its cmake for using correct CMAKE_HIP_ARCHITECTURES.
https://github.com/mfem/mfem/pull/5051
Basically, it needs `set(GPU_TARGETS "${CMAKE_HIP_ARCHITECTURES}" CACHE STRING "HIP targets to compile for" FORCE)`
See CMakeLists-mfem.txt

git clone https://github.com/mfem/mfem
(commit id bf1b25d82e Tue Oct 7 13:22:38 2025)
cd mfem
mkdir build
cd build
CC=`which amdclang` CXX=`which amdclang++` LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${PREFIX}/lib:${PREFIX}/lib64 cmake \
  -DCMAKE_INSTALL_PREFIX=${PREFIX} \
  -DMFEM_USE_OPENMP:BOOL=ON \
  -DMFEM_USE_MPI:BOOL=ON \
  -DMFEM_USE_UMPIRE:BOOL=ON \
  -DCMAKE_CXX_FLAGS="-g" \
  -DMFEM_USE_HIP:BOOL=${ENABLE_HIP} \
  -DCMAKE_HIP_ARCHITECTURES=${HIP_ARCH} \
  -DCMAKE_PREFIX_PATH=/opt/rocm-6.4.2/lib/cmake \
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

When linkinkg fails, use the following command
${CXX} -v -std=c++17 -O3 -fopenmp=libomp -o laghos laghos.o laghos_assembly.o laghos_solver.o -L${PREFIX}/lib -L/opt/rocm-6.4.2/lib -L/lib64 -lmfem ${PREFIX}/lib/libmetis.a ${PREFIX}/lib64/libHYPRE.a ${PREFIX}/lib/libumpire.a ${PREFIX}/lib/libcamp.a -lrocsparse -lrocrand -lrocsolver -lrocblas -lhipblas -lhipsparse -lamdhip64 -lomp -lpthread -ldl -Wl,-rpath,"/opt/rocm-6.4.2/lib" -Wl,-rpath,/lib64

Alternatively, there is a fork that supports cmake build of laghos
https://github.com/helloworld922/Laghos
(commit id 1ead23e Fri Oct 17 13:10:18 2025)
In addition, there is a PR for mfem to fix its cmake for using correct CMAKE_HIP_ARCHITECTURES.
https://github.com/mfem/mfem/pull/5051
Basically, it needs `set(GPU_TARGETS "${CMAKE_HIP_ARCHITECTURES}" CACHE STRING "HIP targets to compile for" FORCE)`
See CMakeLists-mfem.txt

CC=`which amdclang` CXX=`which amdclang++` cmake -DCMAKE_INSTALL_PREFIX=${PREFIX} -DMFEM_USE_HIP=ON -DCMAKE_HIP_ARCHITECTURES=${HIP_ARCH} -DGPU_TARGETS=${HIP_ARCH} ..
