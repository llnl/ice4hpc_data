No GPU. CPU only

MPI is supported with or without OpenMP

git clone https://git.cels.anl.gov/hacc/SWFFT.git
(commit id 203c595 Fri Sep 17 08:18:11 2021)

module load gcc/13.3.1-magic cray-mpich/9.0.1 cray-fftw/3.3.10.11

export DFFT_FFTW_HOME=/opt/cray/pe/fftw/3.3.10.11/x86_trento
cd SWFFT
make -j 8
make -j 8 -f GNUmakefile.openmp
