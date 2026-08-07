#!/bin/bash

ff=`awk 'BEGIN{FS=","}{print $2}' ds_train.csv | sort | uniq | grep -v app`

for f in $ff
do
  echo $f
  awk \
  'BEGIN { \
     FS = "[[:space:]]*,[[:space:]]*"; \
   } \
   (NR == 1) { \
     nf = NF; \
   } \
   ((NR > 1) && ($2 == "'$f'")) \
   { \
     machine = $1; \
     app = $2; \
     \
     num_args_with_comma = NF - nf; \
     args = $3; \
     for (i = 1; i <= num_args_with_comma; i++) { \
       args = args "," $(3+i); \
     } \
     \
     rank = $(4 + num_args_with_comma);
     t = $(20 + num_args_with_comma);

     if (num_args_with_comma == 0)
       printf("%s,%s,%s,\"%s\",%s\n", machine, rank, app, args, t);
     else
       printf("%s,%s,%s,%s,%s\n", machine, rank, app, args, t);
   }' ds_train.csv > $f.txt
done
