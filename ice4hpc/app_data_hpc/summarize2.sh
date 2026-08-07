#!/bin/bash

input_file=ds_train_updated.csv
output_file=merged.txt
Apps="amg|kripke.exe|laghos|miniFE.x|miniVite|TestDfft|XSBench"
nf=`awk 'BEGIN{FS=","} (NR==1){print NF} (NR>1){exit}' ${input_file}`

grep -E "${Apps}" ${input_file} | sort -t ',' -k1,1 -k2,2 | awk -v nf=${nf} \
  'BEGIN {
     FS = "[[:space:]]*,[[:space:]]*";
   }
   {
     machine = $1;
     app = $2;

     num_args_with_comma = NF - nf;
     args = $3;
     for (i = 1; i <= num_args_with_comma; i++) {
       args = args "," $(3+i);
     }

     rank = $(4 + num_args_with_comma);
     t = $(20 + num_args_with_comma);

     if (num_args_with_comma == 0)
       printf("%s,%s,%s,\"%s\",%s\n", machine, rank, app, args, t);
     else
       printf("%s,%s,%s,%s,%s\n", machine, rank, app, args, t);
   }' | sort -t ',' -k1,1 -k3,3 -k2,2n -k4,4g > ${output_file}
