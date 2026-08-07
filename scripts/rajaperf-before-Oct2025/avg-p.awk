#!/usr/bin/awk -f
# This is called by omp-c.sh internally
# When only_avg is set to 1, it will only show the final average.
# Otherwise, it will show all the lines as well as the final average.

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
    nt = $2; # The number of OMP threads used

    if (seen[machine] == 0) { # If true, a new machine is detected.
        n_m++; # id of the new machine or the number of machines recognized
        name[n_m] = machine; # The name of the new machine
    }
    seen[machine] = 1;

    if (seen_nts[machine" "nt] == 0) {
        seen_nts[machine" "nt] = 1;
        nnts[machine] ++;  # The number of different numbers of threads used on this machine
        nts[machine" "nnts[machine]] = nt; # (machine, nts_id) -> nt
    }

    for (i=5; i <= NF; i++) {
        if ($i ~ /^[[:space:]]*-?[0-9]+(\.[0-9]+)?[[:space:]]*$/) { # check if numeric?
            s[machine" "nt" "i] = 0.0 + s[machine" "nt" "i] + $i
            cnt_f[machine" "nt" "i] ++;
        }
    }
}

END {
    print "AVERAGE"
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        if (machine ~ /machine/) continue
        for (k=1; k <= nnts[machine]; k++) {
            nt = nts[machine" "k];
            printf("%s%s%d,,", machine, OFS, nt);
            for (i=5; i <= NF; i++) {
                c = cnt_f[machine" "nt" "i];
                if (c > 0)
                    printf("%s%f", OFS, s[machine" "nt" "i]/(1.0*c));
                else
                    printf("%s", OFS);
            }
            printf("\n");
        }
    }
}
