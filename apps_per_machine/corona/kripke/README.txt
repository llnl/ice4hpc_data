git clone git@github.com:LLNL/Kripke.git

module load rocm/6.3.1 clang/19.1.3-magic cmake/3.30.5 mvapich2/2.3.7


export HSA_OVERRIDE_GFX_VERSION=9.0.0
export PREFIX=/p/lustre1/yeom2/apps/install-corona
export ENABLE_CUDA=OFF
export ENABLE_HIP=ON
export HIP_ARCH="gfx906;gfx900"
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/usr/tce/packages/mvapich2/mvapich2-2.3.7-clang-19.1.3-magic/lib

-------------
Umpire:
-------------
git clone https://github.com/LLNL/Umpire.git
cd Umpire
git submodule update --init

# note that an extra option is added: GPU_TARGETS=
CC=`which amdclang` CXX=`which amdclang++` cmake -S . -B build \
  -DUMPIRE_ENABLE_C=ON \
  -DUMPIRE_ENABLE_TOOLS=OFF \
  -DENABLE_HIP=${ENABLE_HIP} \
  -DCMAKE_HIP_ARCHITECTURES=${HIP_ARCH} \
  -DGPU_TARGETS=${HIP_ARCH} \
  -DAMDGPU_TARGETS=${HIP_ARCH} \
  -DENABLE_BENCHMARKS=OFF \
  -DENABLE_EXAMPLES=OFF \
  -DENABLE_DOCS=OFF \
  -DENABLE_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_FLAGS="-g" \
  -DCMAKE_INSTALL_LIBDIR=${PREFIX}/lib \
  -DCMAKE_INSTALL_PREFIX=${PREFIX} \
  -DCMAKE_PREFIX_PATH=/opt/rocm-6.3.1

cmake --build build -j
cmake --install build
export umpire_DIR=${PREFIX}
export UMPIRE_DIR=${PREFIX}

-------------
Kripke:
-------------

git clone git@github.com:LLNL/Kripke.git
(commit id 8cf3843 Sat Jul 5 16:48:51 2025)

Build:
  Edit CMakeLists.txt to add the MPI header location
    target_include_directories(kripke PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        /usr/tce/packages/mvapich2/mvapich2-2.3.7-gcc-13.3.1-magic/include
        $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>)

  cd Kripke; mkdir build; cd build
  copy llnl-toss4-MI50-rocm6.3.1.cmake to the build directory
  # Note that AMD_GPU_TARGETS is an incorrect variable name. It is supposed to be AMDGPU_TARGETS
  CC=`which amdclang` CXX=`which amdclang++` cmake -DENABLE_MPI=ON -DENABLE_HIP=ON -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g" -C llnl-toss4-MI50-rocm6.3.1.cmake ..
  make -j 16

Run:
  module load rocm/6.3.1
  #export HSA_XNACK=1
  #export MPICH_GPU_SUPPORT_ENABLED=1
  ./kripke.exe
  flux run -n 1 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe
  flux run -n 4 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe --procs 1,2,2
  flux run -n 4 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe --procs 1,2,4 
