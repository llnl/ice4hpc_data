#!/bin/bash

# This script defines various mappings used in may scripts.
# Sharing this would make the definitions consistent across
# different scripts.

# Helper: join enums with a delimiter ':'
key() {
    echo "$1:$2"
}

# Machine name string
declare -A mach
mach[borax]="borax"
mach[boraxo]="boraxo"
mach[dane]="dane"
mach[mammoth]="mammoth"
mach[matrix]="matrix"
mach[corona]="corona"
mach[tioga]="tioga"
mach[tuolumne]="tuolumne"

# Scheduler of the platform
declare -A scheduler
scheduler[borax]="slurm"
scheduler[boraxo]="slurm"
scheduler[dane]="slurm"
scheduler[mammoth]="slurm"
scheduler[matrix]="slurm"
scheduler[corona]="flux"
scheduler[tioga]="flux"
scheduler[tuolumne]="flux"

# Launcher (srun, flux run) options specific to the GPU platform
# To run cpu-only jobs on a GPU-enabled platforms, these options should be turned off
declare -A gpu_opts
gpu_opts[borax]=""
gpu_opts[boraxo]=""
gpu_opts[dane]=""
gpu_opts[mammoth]=""
if [ "${CPU_ONLY}" == 1 ] ; then
gpu_opts[corona]=""
gpu_opts[matrix]=""
gpu_opts[tioga]=""
gpu_opts[tuolumne]=""
else
gpu_opts[matrix]="--gpus-per-task=1"  # Slurm option
gpu_opts[corona]="--gpus-per-task=1 -o gpu-affinity=per-task"  # Flux options
gpu_opts[tioga]="--gpus-per-task=1 -o gpu-affinity=per-task"
gpu_opts[tuolumne]="--gpus-per-task=1 -o gpu-affinity=per-task"
fi

# The name of application subdirectory under the base dir
declare -A app_dir
app_dir[amg]="amg"
#app_dir[CoMD]="CoMD"
app_dir[kripke]="kripke"
app_dir[laghos]="laghos"
app_dir[miniFE.x]="miniFE"
app_dir[miniVite]="miniVite"
app_dir[TestDfft]="SWFFT"
app_dir[XSBench]="XSBench"

# The file name of the application executable
declare -A app_exe
app_exe[amg]="amg"
#app_exe[CoMD]="CoMD-openmp-mpi"
app_exe[kripke]="kripke.exe"
app_exe[laghos]="laghos"
app_exe[miniFE.x]="miniFE.x"
app_exe[miniVite]="miniVite"
app_exe[TestDfft]="TestDfft"
app_exe[XSBench]="XSBench"

# Whether the app supports GPUs
declare -A app_gpu
app_gpu[amg]=0
#app_gpu[CoMD]=0
app_gpu[kripke]=1
app_gpu[laghos]=1
app_gpu[miniFE.x]=1 # native for cuda and with '-openmp45' and '-openmp45-opt' for rocm
app_gpu[miniVite]=0
app_gpu[TestDfft]=0
app_gpu[XSBench]=1 # native cuda and hip support. also with '-openmp-offloading'

# Whether the app supports MPI
declare -A app_mpi
app_mpi[amg]=1 # MPI+OpenMP
#app_mpi[CoMD]=0 # MPI+OpenMP
app_mpi[kripke]=1
app_mpi[laghos]=1
app_mpi[miniFE.x]=1
app_mpi[miniVite]=1 # MPI+OpenMP
app_mpi[TestDfft]=1 # MPI is supported with or without OpenMP
app_mpi[XSBench]=0 # Not supported for cuda and hip. However, it is supported for openmp-offload and openmp-threading.

# Whether the app supports OpenMP
declare -A app_omp
app_omp[amg]=1 # MPI+OpenMP
#app_omp[CoMD]=0 # MPI+OpenMP
app_omp[kripke]=0
app_omp[laghos]=0
app_omp[miniFE.x]=1 # with '-openmp' and '-openmp-opt' for CPU and also with '-openmp45' and '-openmp45-opt' for GPU
app_omp[miniVite]=1 # MPI+OpenMP
app_omp[TestDfft]=0 # with '-openmp' i.e., MPI+OpenMP
app_omp[XSBench]=1 # supported with '-openmp-threading' for CPU as well as with '-openmp-offloading' for GPU

# Application executable variation
declare -A app_var
#app_var[amg]=""
#app_var[CoMD]="-openmp-mpi"
#app_var[kripke]="kripke.exe"
#app_var[laghos]="-serial"
if [ "${CPU_ONLY}" == 1 ] ; then
  app_var[miniFE.x]="-ref"
  # This will overrides any app_var["$(key miniFE.x machine)"]
fi
#app_var[miniFE.x]="-openmp"
#app_var[miniFE.x]="-openmp-opt"
#app_var[miniFE.x]="-openmp45"
#app_var[miniFE.x]="-openmp45-opt"
#app_var[miniVite]=""
#app_var[TestDfft]="-openmp"
#app_var[XSBench]="-openmp-offloading"
if [ "${CPU_ONLY}" == 1 ] ; then
  app_var[XSBench]="-openmp-threading"
fi

app_var["$(key miniFE.x borax)"]="-ref"
app_var["$(key miniFE.x boraxo)"]="-ref"
app_var["$(key miniFE.x dane)"]="-ref"
app_var["$(key miniFE.x mammoth)"]="-ref"
app_var["$(key miniFE.x matrix)"]=""
app_var["$(key miniFE.x corona)"]="-openmp45"
app_var["$(key miniFE.x tioga)"]="-openmp45"
app_var["$(key miniFE.x tuolumne)"]="-openmp45"

# Declare an associative array for architecture specific arguments where the key is a pair of app and machine
declare -A arg_arch
if [ "${CPU_ONLY}" == 1 ] ; then
  arg_arch["$(key kripke corona)"]="--arch Sequential"
  arg_arch["$(key kripke tioga)"]="--arch Sequential"
  arg_arch["$(key kripke tuolumne)"]="--arch Sequential"
  arg_arch["$(key kripke matrix)"]="--arch Sequential"
else
  arg_arch["$(key kripke corona)"]="--arch HIP"
  arg_arch["$(key kripke tioga)"]="--arch HIP"
  arg_arch["$(key kripke tuolumne)"]="--arch HIP"
  arg_arch["$(key kripke matrix)"]="--arch CUDA"
fi
arg_arch["$(key kripke borax)"]="--arch Sequential"
arg_arch["$(key kripke boraxo)"]="--arch Sequential"
arg_arch["$(key kripke dane)"]="--arch Sequential"
arg_arch["$(key kripke mammoth)"]="--arch Sequential"

if [ "${CPU_ONLY}" == 1 ] ; then
  arg_arch["$(key laghos corona)"]="-d cpu"
  arg_arch["$(key laghos tioga)"]="-d cpu"
  arg_arch["$(key laghos tuolumne)"]="-d cpu"
  arg_arch["$(key laghos matrix)"]="-d cpu"
else
  arg_arch["$(key laghos corona)"]="-d gpu"
  arg_arch["$(key laghos tioga)"]="-d gpu"
  arg_arch["$(key laghos tuolumne)"]="-d gpu"
  arg_arch["$(key laghos matrix)"]="-d gpu"
fi
# No `-d` option defaults to cpu. Thus, no need for explicit CPU-only plaforms

arg_arch["$(key XSBench borax)"]="-t 1"
arg_arch["$(key XSBench boraxo)"]="-t 1"
arg_arch["$(key XSBench dane)"]="-t 1"
arg_arch["$(key XSBench mammoth)"]="-t 1"

# with app_var '-openmp-threading'
if [ "${app_var[XSBench]}" == "-openmp-threading" ] ; then
  arg_arch["$(key XSBench corona)"]="-t 1"
  arg_arch["$(key XSBench tioga)"]="-t 1"
  arg_arch["$(key XSBench tuolumne)"]="-t 1"
  arg_arch["$(key XSBench matrix)"]="-t 1"
fi

# Declare an associative array for architecture specific env variable where the key is a pair of app and machine
declare -A env_arch
# The below line needs to be on actual corona system with all the environment set correctly.
env_arch["$(key kripke corona)"]="export HSA_XNACK=1; export HSA_OVERRIDE_GFX_VERSION=9.0.0; export LD_LIBRARY_PATH='${LD_LIBRARY_PATH}:$(dirname $(dirname `which mpicc`))/lib'"
env_arch["$(key kripke tioga)"]="export HSA_XNACK=1"
env_arch["$(key kripke tuolumne)"]="export HSA_XNACK=1"

# Declare an associative array for application specific env setup commands where the key is a pair of app and machine
declare -A env_app
env_app["$(key TestDfft corona)"]="module load fftw"
env_app["$(key TestDfft tioga)"]="module load cray-fftw/3.3.10.11"
env_app["$(key TestDfft tuolumne)"]="module load cray-fftw/3.3.10.11"

# HPCToolkit measurement events
declare -a hpcrun_events=(
    "-e PAPI_BR_INS -e PAPI_LD_INS -e PAPI_SR_INS -e PAPI_TOT_INS"
    "-e PAPI_L1_LDM -e PAPI_L1_STM -e PAPI_L2_LDM -e PAPI_L2_STM -e EPT"
    "-e bdw_ep::FP_ARITH:SCALAR_SINGLE -e bdw_ep::FP_ARITH:SCALAR_DOUBLE -e bdw_ep::ARITH" 
    "-e IO -e PAPI_MEM_WCY -e REALTIME"
)
