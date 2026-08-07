#!/bin/bash

function timestamp {
  date +"%Y-%m-%dT%H:%M:%S"
}

function nanotimestamp {
  date +"%s%N"
}

function diff_hours {
  difference=$(( $(date -d "$2" "+%s") - $(date -d "$1" "+%s") ))
  echo "scale=4 ; ${difference}/3600" | bc
}

function diff_minutes {
  difference=$(( $(date -d "$2" "+%s") - $(date -d "$1" "+%s") ))
  echo "scale=4 ; ${difference}/60" | bc
}

function diff_millisecs {
  echo $1 $2 | awk '{printf("%.3f msec\n", ($2-$1)/1000000.0)}'
}
