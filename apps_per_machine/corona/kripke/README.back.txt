git clone git@github.com:LLNL/Kripke.git

module load gcc/13.3.1-magic mvapich2/2.3.7 cmake/3.30.5


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
  -DCMAKE_PREFIX_PATH=/opt/rocm-6.4.2/lib/cmake

cmake --build build -j
cmake --install build
export umpire_DIR=${PREFIX}
export UMPIRE_DIR=${PREFIX}

-------------
Kripke:
-------------

Build:
  Edit CMakeLists.txt to add the MPI header location
    target_include_directories(kripke PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
        /usr/tce/packages/mvapich2/mvapich2-2.3.7-gcc-13.3.1-magic/include
        $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}/include>)

  cd Kripke; mkdir build; cd build
  copy llnl-toss4-MI50-rocm6.4.2.cmake to the build directory
  CC=`which amdclang` CXX=`which amdclang++` cmake -DENABLE_MPI=ON -DENABLE_HIP=ON -DCMAKE_CXX_FLAGS="-g" -DCMAKE_C_FLAGS="-g" -C llnl-toss4-MI50-rocm6.4.2.cmake ..
  make -j 16

Run:
  module load rocm/6.4.2 rocmcc/6.4.2-cce-20.0.0-magic
  export HSA_XNACK=1
  export MPICH_GPU_SUPPORT_ENABLED=1
  ./kripke.exe
  flux run -n 1 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe
  flux run -n 4 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe --procs 1,2,2
  flux run -n 4 -N 1 --gpus-per-task=1 --exclusive -o cpu-affinity=per-task -o gpu-affinity=per-task -o mpibind=off ./kripke.exe --procs 1,2,4 
