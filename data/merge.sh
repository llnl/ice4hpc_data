#!/bin/bash
# Merge all the `result.<machine>.txt` files into one single file

input_files=`ls -1 result.*.txt`
output_file=merged.txt

awk \
'BEGIN {
  FS = "[[:space:]]*,[[:space:]]*"
  OFS = ","
  IGNORECASE=1
  app_name["amg"] = "amg"
  app_name["kripke"] = "kripke.exe"
  app_name["laghos"] = "laghos"
  app_name["miniFE"] = "miniFE.x"
  app_name["miniVite"] = "miniVite"
  app_name["SWFFT"] = "TestDfft"
  app_name["XSBench"] = "XSBench"
}

{
  gsub("  ", " ")
  gsub(" ,", ",")
  gsub(" \"", "\"")

  app = $1
  machine = $2
  rank = $3

  num_args_with_comma = NF - 5
  args = $4
  for (i = 1; i <= num_args_with_comma; i++) {
    args = args "," $(4+i)
  }

  if (app ~ /kripke/) {
    if ((machine == "tuolumne") || (machine == "tioga") || (machine == "corona")) {
      sub("--arch HIP", "", args)
    } else if (machine == "matrix") {
      sub("--arch CUDA", "", args)
    } else {
      sub("--arch Sequential", "", args)
    }
  } else if (app ~ /laghos/) {
    if ((machine == "tuolumne") || (machine == "tioga") || (machine == "corona") || (machine == "matrix")) {
      sub("-d gpu", "", args)
    } else {
      sub("-d cpu", "", args)
    }
  } else if (app ~ /XSBench/) {
    pos = index(args, "-t ")
    if (pos > 0) {
      if (length(args) > pos + 3) {
        cpu = sub("-t 1 ", "", args);
        if (cpu == 0) {
          cpu = sub(" -t 1\"", "\"", args);
          if (cpu == 0) {
            cpu = sub("\"-t 1\"", "\"\"", args);
          }
        }
      } else {
        cpu = sub("-t 1", "", args)
      }

      if (cpu == 0) {
        # Skip printing out the samples with `-t 32` and `-t 56` as there is nothing to match
        next
      }
    }
  }

  gsub("  ", " ", args)
  gsub(/[[:space:]]+$/, "", args)
  gsub(" ,", ",", args)
  gsub(" \"", "\"", args)

  t = $NF

  printf("%s,%s,%s,\"%s\",%s\n", machine, rank, app_name[app], args, t);
}' ${input_files} | sort -t ',' -k1,1 -k3,3 -k2,2n -k4,4g > ${output_file}
