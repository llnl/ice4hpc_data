#!/usr/bin/awk -f
# This is called by gpu.sh, seq-c.sh and seq-g.sh internally.
# When only_avg is set to 1, it will only show the final average.
# Otherwise, it will show all the lines as well as the final average,
# and this is the default behavior

BEGIN {
  FS = "[[:space:]]*,[[:space:]]*"
  OFS = ","
}

{
    if (NR == 1) {
        print $0
        next
    }
    if (only_avg == 0)
        print $0

    machine = $1;

    if (seen[machine] == 0) {
        n_m++;
        name[n_m] = machine;
    }
    seen[machine] ++;
    for (i=2; i <= NF; i++) {
        # Only use the values that are valid and avoid 'NaN' or 'Not run'
        if ($i ~ /^[[:space:]]*-?[0-9]+(\.[0-9]+)?[[:space:]]*$/) { # check if numeric?
            # Sum of the values of the kernel performance on the machine
            s[machine" "i] = 0.0 + s[machine" "i] + $i
            # Count the number of values summed up so far
            cnt_f[machine" "i] ++;
        }
    }
}

END {
    print "AVERAGE"
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        if (machine ~ /machine/) continue
        printf("%s", machine);
        for (i=2; i <= NF; i++) {
            c = cnt_f[machine" "i];
            if (c > 0)
                printf("%s%f", OFS, s[machine" "i]/(1.0*c));
            else
                printf("%s", OFS);
        } 
        printf("\n");
    }
}
