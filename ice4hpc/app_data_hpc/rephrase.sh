#!/bin/bash

# Remove runtime-environment-specific arguments in the sample such that samples
# can be matched for comparison by the same problem-specific arguments.
# If a sample is from running an application on a GPU-enabled platform
# while using only CPUs, this script will change the machine name to *-cpu,
# e.g., lassen -> lassen-cpu, corona -> corona-cpu
# There are applications that can leverage GPUs:
# e.g., kripke, laghos, miniFE and XSBench.
# Among these kripke, laghos and XSBench take arguments specific to the runtime
# environment, such as `-d gpu`,`--arch CUDA`, and `-t 32`.
# For all other applications, the name of a GPU-enabled machine name must be
# appended with "-cpu".

data_file=ds_train.csv
new_file=ds_train_updated.csv
gpu_machines="corona lassen"

if [ ! -f ${data_file} 2> /dev/null ] ; then
  echo "${data_file} does not exist!"
fi

head -n 1 ${data_file} > ${new_file}

awk -v gpu_machines="${gpu_machines}" \
'BEGIN{
  FS = "[[:space:]]*,[[:space:]]*"
  OFS = ","
  IGNORECASE=1
  n_gpums = split(gpu_machines, gpu_machine, " ")
} 
(NR == 1) {
  nf = NF
}
(NR > 1) {
  cpu = 0
  gpu = 0

  num_args_with_comma = NF - nf
  args = $3
  for (i = 1; i <= num_args_with_comma; i++) {
    args = args "," $(3+i)
  }
  # Any access to beyond $3 needs to consider (NF - nf)
  t = $(20 + num_args_with_comma)
  if (t == "") next

  if ($2 ~ /kripke/) {
    # kripke arguments include --procs x,y,z which will confuse the number of fields parsed
    if (index(args, "--arch")) {
      cpu = sub("--arch Sequential", "")
      if (cpu == 0) { // not sequential
        if ($1 ~/lassen/) {
          gpu = sub("--arch CUDA", "")
        } else if ($1 ~/corona/) {
          gpu = sub("--arch HIP", "")
        }
        if (gpu == 0) {
          print "--arch option not recognized at line " NR
          exit
        }
      } else { // sequential
        for (ig = 1; ig <= n_gpums; ig++) {
          if ($1 == gpu_machine[ig]) {
            $1 = $1"-cpu";
            break;
          }
        } 
      }
    } else { # Assume the default is CPU (without --arch)
      for (ig = 1; ig <= n_gpums; ig++) {
        if ($1 == gpu_machine[ig]) {
          $1 = $1"-cpu";
          break;
        }
      } 
    }
  } else if ($2 ~ /laghos/) {
    gpu = sub("-d gpu", "")
    cpu = sub("-d cpu", "")
    if (gpu == 0) { # Assume the default is CPU
      for (ig = 1; ig <= n_gpums; ig++) {
        if ($1 == gpu_machine[ig]) {
          #if (($1 == "corona") && ($20 < 0.006)) {
          if (($1 == "corona") && ($20 < 0.011)) {
            # laghos runs on corona-cpu that took only 0.00502 are all failed runs
            next
          }
          $1 = $1"-cpu";
          break;
        }
      } 
    } else {
      if (cpu != 0) {
        print "Cannot have conflicting arguments at line " NR
        exit
      }
      if (($1 !~ /lassen/) && ($1 !~ /corona/)) {
        print "Unknown gpu machine $1 at line " NR
        exit
      }
    }
  } else if ($2 ~ /XSBench/) {
    # Remove samples with the argument `-t 32` or `-t 56` using a single rank
    # and 32/56 OpenMP threads because we do not have any other runs that can
    # match for relative performance calculation.
    # `-t` option is only available for CPU only build.

    pos = index(args, "-t ")
    if (pos > 0) {
      if (length(args) > pos + 3) {
        cpu = sub("-t 1 ", "");
        if (cpu == 0) {
          cpu = sub(" -t 1\"", "\"");
          if (cpu == 0) {
            cpu = sub("\"-t 1\"", "\"\"");
          }
        }
      } else {
        cpu = sub("-t 1", "")
      }

      if (cpu == 0) {
        # Skip printing out the samples with `-t 32` and `-t 56`
        next
      }
      # The actual GPU build, with native CUDA/HIP, does not take `-t` option.
      for (ig = 1; ig <= n_gpums; ig++) {
        if ($1 == gpu_machine[ig]) {
          $1 = $1"-cpu";
          break;
        }
      } 
    }
  } else if ($2 ~ /miniFE/) {
    # Based on the inspection of execution times, I believe that the miniFE runs
    # on corona were using CPUs. I see similar times myself using corona CPUs.
    # However, the lassen runs were faster. Since I do not believe power9 would
    # perform better than the Xeon of quartz or ruby, I have believe that those
    # were GPU runs.
    if ($1 ~ /corona/) {
      $1 = $1"-cpu"
    }
  } else if ($2 ~ /miniVite/) {
    if ($1 ~ /corona/) {
      # All these miniVite runs on corona took around 0.005 seconds and
      # were almost 20x times faster than the latest measurements.
      # This is quite suspicious that the runs might have all failed.
      next
    }
    for (ig = 1; ig <= n_gpums; ig++) {
      if ($1 == gpu_machine[ig]) {
        $1 = $1"-cpu";
        break;
      }
    }
  } else if (($2 ~ /amg/) || ($2 ~ /sw4lite/) || ($2 ~ /TestDfft/)) {
    # These apps do not use GPU at all.
    for (ig = 1; ig <= n_gpums; ig++) {
      if ($1 == gpu_machine[ig]) {
        $1 = $1"-cpu";
        break;
      }
    } 
    if (($1 ~ /corona/) && ($2 ~ /amg/)) {
      # REALTIME of these samples are very different from those of the latest measurements,
      # suggesting that the jobs did not complete successfully.
      # Some did not run at all, reporting no REALTIME.
      next
    }
  }

  gsub("  ", " ")
  gsub(" ,", ",")
  print $0
}' ${data_file} | sort -t ',' -k1,1 -k2,2 >> ${new_file}
