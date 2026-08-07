#!/bin/bash


#borax,32,amg,"-problem 1 -P 4 4 2 -n 128 128 64",27.971479
#corona-cpu,TestDfft,20 120,1,0.0833,3232000000.0,3756130352.0,2500344019.0,19900000000.0,679641068.0,-1.0,-1.0,-1.0,-1.0,-1.0,-1.0,293744.0,212112.0,7583160328.0,3.2125320000000013,,,,1.785467999999999
#machine,app,args,ranks

awk \
'BEGIN {FS=",";OFS=","}

(FNR==1) {
  fcnt ++
  nf = NF
}

(fcnt == 1) {
  cnt1 ++
  Ncs_args = NF - nf
  Machine = $1
  Nnodes = $2
  App = $3
  Args = $4
  if (Ncs_args > 0) {
    for (i=1; i <= Ncs_args; i++) {
      Args = Args","$(i+4)
    }
  }
  Texec = $(5+Ncs_args)
  if (Texec > 0) {
    run[Nnodes " " App " " Args] ++
  }
  machs[Machine] = 1
}

(fcnt == 2) {
  cnt2 ++
  Ncs_args = NF - nf
  Machine = $1
  Nnodes = $(4+Ncs_args)
  App = $2

  Args = $3
  if (Ncs_args > 0) {
    for (i=1; i <= Ncs_args; i++) {
      Args = Args","$(i+3)
    }
  }

  gsub(/^"|"$/, "", Args)
  Args = "\"" Args "\""

  if (Ncs_args > 0) {
    n = split(Args, cs_args, ",")
    if (n != Ncs_args + 1) {
      print "split failed"
      exit
    }
    for (i = 1; i <= n; i++)
      $(i+2) = cs_args[i]
  } else {
    $3 = Args
  }

  Texec = $(20+Ncs_args)  # $20
  if ((Texec > 0) && (run[Nnodes " " App " " Args] > 0)) {
    print $0 > "preserved.txt"
  } else {
if (App == "laghos") print Nnodes, App, Args
    print $0 > "removed.txt"
    cnt3 ++
  } 
}

END {
  printf("Number of new samples: %u\nNumber of old samples: %u\nNumber of removed samples: %u\n", cnt1, cnt2, cnt3) > "/dev/stderr"
}
' merged.txt ../ice4hpc/app_data_hpc/ds_train_updated.csv
