#!/bin/bash

cmd_file=uniq_app_arg_rank.txt
mkdir -p app_cmd
apps="amg
XSBench
miniFE.x
TestDfft
laghos
miniVite
kripke.exe"

ranks="1 32"

for app in ${apps}
do
  for rank in ${ranks}
  do
    of=app_cmd/cmd_${app}.${rank}.txt
    grep "${app}, ${rank}," ${cmd_file} | sed -E "s/${app}, ${rank},/${app}/" > ${of}
  done
done

