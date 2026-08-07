- Each file name is in the format of NN-rep<R>-sz<S>, where R is the value of
  `--repfact` parameter for `rajaperf.exe` and S is the value of `--sizefact`.
- Each file has AVERAGE section at the bottom. rajeperf.exe may have run multiple
  times with the same parameter choice.
- Old version of rajaperf reported less number of kernels. So, merging the new set
  with an older set might require dropping the values regarding the kernels added
  recently.

- seq-c-rep<R>-sz<S>: Kernel timing results (Base_Seq/default) from CPU-only runs.
  This includes the results from CPU-only runs using the rajaperf executable
  built for only CPUs on GPU-enabled platforms.
  There is unexplained difference between this and the results shown in seq-g.
  I think for the purpose of representing the performance of CPU-only executions
  on GPU-capable platforms, this dataset makes more than the other one.

- seq-g-rep<R>-sz<S>: Kernel timing results (Base_Seq/default) from GPU-enabled runs.

- gpu-rep<R>-sz<S>: GPU kernel timing results (the first variant of either
  Base_CUDA or Base_HIP) from GPU-enabled runs.

- omp-rep<R>-sz<S>: Kernel timing results (Base_OpenMP/default) from CPU-only
  runs with OpenMP enabled.

- summary.txt: Each measurement was performed multiple times. This file lists
  the results of the relevant kernels on each machine, and shows the average of
  each case at the end of the file.

- common_kernels.txt: This file includes the list of kernels that are used in
  both the latest and older versions of RAJAPerfSuite. There are total 62 kernels.

- machine_rep.txt: As there were 3 different --sizefact arguments (0.5, 1.0, 2.0)
  and only one --repfact argument (0.5) used, there are three sets of results.
  We picked 62 kernel values from each and concatenated them.
  That makes 186 values plus the machine name.
