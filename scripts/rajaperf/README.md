The structure of the data directory assumed is machine/repeat_no/repfact-sizefact[-omp_num_threads].

## To run tests:
  For example, for borax

  ```
  cd borax
  salloc -N 1 --exclusive -ppdebug
  cat /proc/cpuinfo > cpuinfo.txt
  lscpu > lscpu.txt
  cat /sys/devices/system/cpu/smt/active >  cpu_smt_active.txt
  exit
  ```
  Take a look at how many cores there are, and set `num_smt_cores` in `exp.sh`

  ```
  mkdir 1 2 3
  cd 1;
  ../exp.sh; cp ../sbatch.sh .; sbatch sbatch.sh
  cd ../2;
  ../exp.sh; cp ../sbatch.sh .; sbatch sbatch.sh
  cd ../3;
  ../exp.sh; cp ../sbatch.sh .; sbatch sbatch.sh
  ```

## To gather data:
  - First run `filter.sh`, which will run `filter.awk` on `RAJAPerf-timing-Average.csv` unsder each data directory.
  - Then, run `seq-c.sh`, `seq-g.sh`, `gpu.sh` and `omp-c.sh`, which are independent and thus can be executed in any order among them.
  - Finally, run `summarize.s`. This generates `summary.txt`

## Machine representation vectors
  - As RAJAPerf has updated the set of kernels, the `summary.txt` may contain columns of different set of kernels.
  - With two different `summary*.txt`, find the common set of kernels.
    - `find_common_kernels.sh >  common_kernels.txt`
  - Then, run `machine_rep.sh` to generate machine representation vectors
