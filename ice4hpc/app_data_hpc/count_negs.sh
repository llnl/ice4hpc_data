#!/bin/bash

awk \
'BEGIN{FS=","}
 (NR==1){
   nf=NF;
   for (i=1; i<=NF; i++){
     label[i] = $i
   }
 }
 (NR>1){
   # Skipping machine,app,args,ranks,duration
   # Also consider the case where args has commas and is counted as multiple fields

   extra_nf_args = NF-nf
   for ( i = extra_nf_args + 6 ; i<=NF; i++) {
     if ($i ~ /^[[:space:]]*-?[0-9]+(\.[0-9]+)?[[:space:]]*$/) { # check if numeric?
       #if (($i != -1) && ($i < 0.0)) {
       if ($i < 0.0) {
         neg[i - extra_nf_args] ++;
       }
     }
   }
 }
 END {
   for (key in neg) {
     print key, label[key], neg[key]
   }
 }' ds_train_updated.csv
