No GPU. CPU only

MPI is supported with or without OpenMP

git clone https://git.cels.anl.gov/hacc/SWFFT.git
(commit id 203c595 Fri Sep 17 08:18:11 2021)

module load gcc/13.3.1-magic cmake/3.30.5 fftw/3.3.10

export DFFT_FFTW_HOME=/usr/tce/packages/fftw/fftw-3.3.10-gcc-10.3.1
cd SWFFT
make -j 8
make -j 8 -f GNUmakefile.openmp
