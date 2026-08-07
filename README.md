# Cross-platform Performance of HPC Applications (ice4hpc data)
This repository maintains artifacts related to the collection of HPC application performance data across various systems. The ultimate goal of this data collection is to develop extensible, cross-platform performance prediction models that can guide intelligent resource management and job scheduling within HPC environments. 

---

## Machines
  - CPU only machines: [boraxo](https://hpc.llnl.gov/hardware/compute-platforms/boraxo), [mammoth](https://hpc.llnl.gov/hardware/compute-platforms/mammoth)  and [dane](https://hpc.llnl.gov/hardware/compute-platforms/dane) 
  - GPU-enabled machines: [matrix](https://hpc.llnl.gov/hardware/compute-platforms/matrix), [tioga](https://hpc.llnl.gov/hardware/compute-platforms/tioga), [tuolumne](https://hpc.llnl.gov/hardware/compute-platforms/tuolumne) 

---

## Applications

### HPC workload benchmarks:
  - [amg](https://github.com/LLNL/AMG)  (original), [kripke](https://github.com/LLNL/Kripke), [laghos](https://github.com/CEED/Laghos), [miniFE](https://github.com/Mantevo/miniFE), [miniVite](https://github.com/ECP-ExaGraph/miniVite), [SWFFT](https://git.cels.anl.gov/hacc/SWFFT), and [XSBench](https://github.com/ANL-CESAR/XSBench)
  - The table below describes how each application was built (some cases resulted in multiple executables):
    | Properties \ Apps | amg | kripke | laghos | miniFE | miniVite | SWFFT | XSBench |
    |--------------------|-----|--------|---------|---------|-----------|--------|----------|
    | **MPI-enabled** | Y | Y | Y | Y | Y | Y | N |
    | **OpenMP-enabled** | Y | N | N | Y | Y | Y/N | Y |
    | **CUDA/HIP-enabled** | N | Y | Y (via MFEM, Hypre, and Umpire) | Y (native CUDA, OpenMP 4.5) | N | N | Y (CUDA, HIP, and OpenMP 4.5) |
    | **CPU-only executable available** | Y | Y (with `--arch Sequential`) | Y (with `-d cpu`) | Y (ref version) | Y | Y | Y |
    | **Other notes** | — | — | — | - MPI is on for all executables.<br>- `openmp45` and `openmp45-opt` built with `clang/19.1.3-magic` and `mpi`.<br>- On AMD GPUs, `openmp45` variant performed slower than sequential version.<br>- These samples are not included. | — | - May require `fftw` or `cray_fftw` module loaded for running jobs. | - MPI not supported for native HIP/CUDA builds, but supported for CPU OpenMP and offloading OpenMP. |
    | **Executables** | - `amg` (MPI+OpenMP) | - `kripke.exe` (MPI and (+CUDA/HIP)) | — | - `miniFE.x` (CUDA)<br>- `miniFE.x-openmp` (MPI+OpenMP)<br>- `miniFE.x-openmp45` (MPI+OpenMP 4.5)<br>- `miniFE.x-ref` (CPU-only) | - `miniVite` (MPI+OpenMP) | - `TestDfft` (MPI)<br>- `TestDfft-openmp` (MPI+OpenMP) | - `XSBench` (CUDA/HIP/CPU-only w/ MPI+OpenMP)<br>- `XSBench-openmp-offloading` (MPI+OpenMP 4.5)<br>- `XSBench-openmp-threading` (CPU-only MPI+OpenMP) |
    | **Modules** | - `gcc/13.3.1-magic`<br>- `mvapich2/2.3.7`<br>- `PrgEnv-gnu`<br>- `cray-mpich/9.0.1` | - `gcc/13.3.1-magic`<br>- `mvapich2/2.3.7 (cuda/12.9.1)`<br>- `rocm/6.4.2`<br>- `rocmcc/6.4.2-cce-20.0.0-magic` | - `cmake/3.30.5` `gcc/13.3.1-magic`<br>- `mvapich2/2.3.7 (cuda/12.9.1)`<br>- `rocm/6.4.2`<br>- `rocmcc/6.4.2-cce-20.0.0-magic`<br>- `cray-mpich/9.0.1` `cmake/3.29.2` | - `gcc/13.3.1-magic`<br>- `mvapich2/2.3.7 (cuda/12.9.1)`<br>- `rocm/6.4.2`<br>- `rocmcc/6.4.2-cce-20.0.0-magic`<br>- `cray-mpich/9.0.1` | - `gcc/13.3.1-magic`<br>- `mvapich2/2.3.7` | - `gcc/13.3.1-magic`<br>- `mvapich2/2.3.7` `fftw`<br>- `cray-mpich/9.0.1`<br>- `cray-fftw/3.3.10.11` | - `gcc/13.3.1-magic`<br>- `(cuda/12.9.1)`<br>-     `rocm/6.4.2`<br>- `rocmcc/6.4.2-cce-20.0.0-magic` |


### Machine characterization benchmark:
  - [RAJAPerfSuite](https://github.com/LLNL/RAJAPerf)
  - ran with 3 different argument combinations:
    - `--repfact` : 0.5
    - `--sizefact` : 0.5, 1.0, 2.0
  - RAJAPerfsuite results will be used to augment the application
    performance sample to describe the machine from which the sample was
    collected
    - For the application performance samples from CPU only machines, we
      can use the numbers in `Base_Seq`/default  column
    - For the application performance samples using only CPUs on
      GPU-enabled machines, we can use the numbers in `Base_Seq`  column
    - For the application performance samples using GPUs, we choose the
      either column of `Base_CUDA`  or `Base_HIP` .
      - Currently only using the first variant of these, such as
        `block256`. However, some kernels only ran with other variants. We
        might have to use those numbers as well.


---

## Job execution strategies
  - All the runs used a **single node**.
  - OpenMP was **not** leveraged although executables were built to use it.
    - Only some of *RAJAPerf* runs used OpenMP.
  - Some runs used 32 MPI ranks as well as a single rank.
  - GPU-enabled runs only used a single rank and no 32-rank run was performed as one rank would drive one GPU and there are only 4 GPUs per
    node.
  - Took median from three runs of each combination (*app, args, rank,
    machine*).
  - Use scripts to create a directory where you want to run jobs and collect performane data
    - Copy [scripts/create_merged_job.sh](scripts/create_merged_job.sh) into that directory
    - Make necessary modifications to
      - Select application and machine
      - Set other relevant variables such as
        - `base`: Where this experimental template is located
        - `exp_base`: The subfolder to be created to host all the job scripts
        - `timeout`: Timeout limit for each job. This will be added to each job script.
        - `num_ranks`: Number of MPI ranks to run jobs with
          - `max_ranks_per_node`: The number of nodes to be used is num_ranks/max_ranks_per_node. 
        - `repeats`: How many time to run each combination of machine, rank, app and args
        - `bank`: job bank on LC. Comment out if not relevant.
    - Then, run the script. This will create job scripts organized in a directroy hierarchy.
      - `<exp_base>/<machine>/<app>/nr<num_rank>/arg_<idx>/job.sh`
      - `arg_<idx>`: maps to each line of the file `cmd_<app>.<num_rank>.txt` under [scripts/app_cmd](scripts/app_cmd)
    - May further need to modify [scripts/maps.sh](scripts/maps.sh).
  - Launch the jobs
    - `sbatch job.sh` on *borax*, *dane*, *mammoth* and *matrix*, or `flux batch job.sh` on *corona*, *tioga* and *tuolumne*
    - For bulk submission, you can try something like 'for i in \`seq 1 186\`; do pushd arg_$i; sbatch job.sh ; popd; done' under <exp_base>/<machine>/<app>/nr<num_rank>
  - Check the completion of jobs: run [check_completion.sh](scripts/check_completion.sh) under `<exp_base>/<machine>/<app>/nr<num_rank>`
  - Gather performance numbers: Copy [scripts/get_all_data.sh](scripts/get_all_data.sh) to where create_merged_job.sh was run, and run it.
  - For *RAJAPerf* runs, copy the whole [scripts/rajaperf](scripts/rajaperf) folder to where you want to run jobs, and follow the instruction in [scripts/rajaperf/README.md](scripts/rajaperf/README.md)

---

## Architecture-specific arguments and environment variables
  | Application | Arguments | Environment Variables |
  |--------------------------|-------------------|----------------------------------------|
  | **All OpenMP capable apps** | *(none)* | `OMP_NUM_THREADS=1` |
  | **kripke** | - `--arch <CUDA\|HIP\|Sequential>`: the default does not seem to be honored but runs as Sequential.<br> - Also, it crashes with `--arch sequential` on `matrix`. With `--arch CUDA`, it runs but the execution time is always around 3.5 sec regardless of the problem size.<br> - It is actually faster in many cases on `tuolumne`. | - `HSA_XNACK=1`<br> - `(MPICH_GPU_SUPPORT_ENABLED=1)`<br> - The developer said it is not supposed to require `HSA_XNACK=1`, but it currently crashes without it on `tuolumne` and `tioga`. |
  | **laghos** | - `-d gpu\|cpu`: the default is `cpu`. | *(none)* |
  | **XSBench** | - `-t <n>`: number of OpenMP threads (only available for `openmp-threading` variant).<br> - Using `-t` on GPU platforms will terminate the app after showing the help page — no real performance result.<br> - History-based simulation not implemented in GPU mode (`-m history` does not work; only `-m event` works).<br> - On `tioga`:<br> &nbsp;&nbsp;• `-m event -s XL -G unionized` and `-m event -s XXL -G unionized`: “GPUassert: out of memory GridInit.cpp 54”<br> - On `tuolumne`:<br> &nbsp;&nbsp;• `-m event -s XXL -G unionized`: “GPUassert: out of memory GridInit.cpp 54”<br> - On `dane`:<br> &nbsp;&nbsp;• `-t 1 -m event -s XXL -G unionized` and `-t 1 -m history -s XXL -G unionized`: “Detected 1 oom_kill event” | *(none)* |


---


## Artifacts: 
  - Build instructions: `apps_per_machine/<machine>/<app>/README.txt`
    - desctibes the environment variables and the modules used as well as the compilation steps
  - Machine specs:
    - The information from `lscpu` and `proc/cpuinfo`, `rocminfo`, `nvidia-smi`, and `/sys/devices/system/cpu/smt/active`
    - Available under `scripts/rajaperf/<machine>`
  - Executables: under `bins_per_machine/<machine>/<app>`
    - `bins_per_machine/<machine>.tar` is tracked by `git lfs`. So, obtain it using `git lfs fetch; git lft checkout`, or `git lfs pull`.
  - Scripts to setup experiments, check job completion and gather data
    samples.
    - [scripts/create_merged_job.sh](scripts/create_merged_job.sh) and [create_job.sh](create_job.sh)
      - [scripts/maps.sh](scripts/maps.sh): defines relevant mappings for handling specifics with certain combinations of application and platforms
    - [scripts/check_completion.sh](scripts/check_completion.sh) : check if the jobs have completed
      successfully based on application-specific outputs.
    - [scripts/get_all_data.sh](scripts/get_all_data.sh) : collects all the execution time measurements
      in the format of (app, machine, rank, args, exec_time in sec)
  - Application arguments used: [scripts/app_cmd](scripts/app_cmd)
  - Data collected: [data](data)
 
---

## Data Curation Caveats

- Certain apps do not use GPUs at all.
  - They are written for MPI/OpenMP parallelization. Whether they run on GPU-enabled platforms or not, they will only use CPUs.
  - Thus, representing the machine where a sample is collected should consider this.  
    For example, *amg*, *miniVite*, and *SWFFT* do not leverage GPUs at all.
  - When choosing *RAJAPerf* results to represent such runs, the **CPU performance results** should be used.
  - *miniFE* offers multiple variations to leverage GPUs, such as:
    - native CUDA, or  
    - device offloading via OpenMP 4.5.  
      In case of HIP devices, OpenMP 4.5 could be used.  
      However, the performance of that was not even as good as the sequential runs.  
      Therefore, we only consider **sequential variation of *miniFE*** for HIP-capable platforms.
  - In the new dataset, we have *RAJAPerf* samples labeled as:
    - `corona-cpu`, `matrix-cpu`, `tioga-cpu`, and `tuolumne-cpu`  
      These are the results of *RAJAPerf* executables built **without CUDA or ROCm**.
      - You can find these results in `summary.txt` or `seq-c-rep*-sz*.txt`.
  - Similarly, `RAJAPerf` reports a `Base_Seq` column even with executables built with CUDA or ROCm, in addition to `Base_CUDA` or `Base_HIP` columns.
    - In the old/new dataset, such results are summarized in `seq-g-rep*-sz*.txt`.
    - With the absence of `lassen-cpu` and old `corona-cpu`, this is the closest alternative.
    - Alternatively, we could use `seq-g` for both old and new data.  
      However, there are performance differences between:
      - `seq-g-rep*-sz*.txt` and  
      - `*-cpu` results in `seq-c-rep*-sz*.txt` or `summary.txt`.  
        - The former is for **consistency**, the latter is for **accuracy**.

- Some application arguments are **platform-specific** rather than input-problem-specific.
  - Matching samples for relative performance calculation involves finding pairs of samples with identical:
    - application name,
    - number of MPI ranks, and
    - general application input arguments.
  - When matching between CPU and GPU runs, **we do not consider the number of MPI ranks.**
  - Platform-specific arguments as below should **not** be considered in matching.
    - `--arch HIP|CUDA|Sequential` (with *Kripke*),
    - `-d gpu|cpu` (with *Laghos*), or
    - `-t 1` (with *XSBench*)

- Some runs in the old dataset may have **terminated without completing successfully**, while still reporting times.
  - During new data collection, the application-specific output of each run was checked to confirm successful completion.  
    Any run that did not generate the expected output was **excluded**.
    - A couple of *XSBench* runs, in particular, resulted in **memory errors**.
    - Some runs of other applications may have **exceeded time limits** in the old dataset.
    - Some codes may have **crashed on GPU platforms**.
      - For example, *Kripke* on *matrix* crashed with `--arch Sequential`.  
        Even runs with `--arch CUDA` were slower than the counterparts on *tioga* and *tuolumne*,  
        which is suspicious since *matrix* usually performs better than those two.

## Authors
- Jae-Seung Yeom
- Daniel Nichols

## Release

- LLNL-DATA-2022879
- License: CC BY 4.0 (Creative Commons Attribution 4.0 International)
