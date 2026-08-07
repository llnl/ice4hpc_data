No GPU, CPU only
mpi

module load PrgEnv-gnu gcc/13.3.1-magic cray-mpich/9.0.1
git clone https://github.com/XiaohuaZhangLLNL/conveyorlc.git

cd conveyorlc
edit Makefile.include to add '-g' and '-Wno-implicit-function-declaration' to INCLUDE_CFLAGS
edit test/Makefile to add '-g' to amg and .o targets

make -j
cd test
