#!/usr/bin/awk -f

# 'filter.sh' calls this script To filter certain columns or rows.

BEGIN {
  FS = "[[:space:]]*,[[:space:]]*"
  OFS = ","
}

function print_line ()
{
  if ($1 ~ /^[[:space:]]*$/) $1 = "";

  if (NF == 31) {
    printf("%s", $1);
    for (i=2; i <= NF; i++) {
      if ($i ~ /^[[:space:]]*$/) $i = "";
      #if (i==3 || i==6) continue
      printf("%s%s", OFS, $i);
    }
    printf("\n");
  } else
  if (NF == 73) {
    printf("%s", $1);
    for (i=2; i <= NF; i++) {
      if ($i ~ /^[[:space:]]*$/) $i = "";
      #if (i==3 || i==6) continue
      printf("%s%s", OFS, $i);
    }
    printf("\n");
  } else
  if (NF == 75) {
    printf("%s", $1);
    for (i=2; i <= NF; i++) {
      if ($i ~ /^[[:space:]]*$/) $i = "";
      #if (i==3 || i==6) continue
      printf("%s%s", OFS, $i);
    }
    printf("\n");
  } else{
    printf("%s", $1);
    for (i=2; i <= NF; i++) {
      if ($i ~ /^[[:space:]]*$/) $i = "";
      printf("%s%s", OFS, $i);
    }
    printf("\n");
  }
}

{
  #if ($1 ~ /Basic_ARRAY_OF_PTRS/) {
  if ($1 ~ /Basic_DAXPY/) {
    is_on = 1;
    print_line()
  #} else if ($1 ~ /Comm_HALO_PACKING_FUSED/) {
  } else if ($1 ~ /Algorithm_MEMCPY/) {
    print_line()
    is_on = 0;
  } else if (is_on == 1) {
    print_line()
  } else if ($1 ~ /Kernel/) {
    print_line()
  }
}
