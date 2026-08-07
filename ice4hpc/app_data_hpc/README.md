# Ice4hpc Data Ver1
Performance counter and execution time data collected by running various HPC applications on multiple HPC platforms.
These samples are collected by Daniel Nichols and Alex Movsesyan.

## Preparation before using them
Run `rephrase.sh`. This script will
Remove runtime-environment-specific arguments in the sample such that samples
can be matched for comparison by the same problem-specific arguments.
If a sample is from running application on a GPU-enabled platform
while using only CPUs, change the machine name to *-cpu,
e.g., lassen -> lassen-cpu, corona -> corona-cpu
There are applications that can leverage GPUs:
e.g., kripke, laghos, miniFE and XSBench.
Among these kripke, laghos and XSBench take arguments specific to the runtime
environment, such as `-d gpu`,`--arch CUDA`, and `-t 32`.
For all other applications, the name of a GPU-enabled machine name must be
appended with "-cpu".
