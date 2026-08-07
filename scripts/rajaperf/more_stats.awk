#!/usr/bin/awk -f
# This is called by omp-c.sh internally
# When only_avg is set to 1, it will only show the final average.
# Otherwise, it will show all the lines as well as the final average.

BEGIN {
  FS = "[[:space:]]*,[[:space:]]*"
  OFS=","
}


{
    print $0

    # Process the average values at the bottom of the input file (or stream)
    if ($1 ~ /^AVERAGE$/) {
        average_starts = 1;
        next
    }
    if (average_starts != 1) {
        next
    }

    machine = $1;
    nt = $2; # The number of OMP threads used

    # Assign index to unique machine names and build machine name map
    if (seen[machine] == 0) { # If true, a new machine is detected.
        n_m++; # id of the new machine or the number of machines recognized
        name[n_m] = machine; # The name of the new machine
        for (i=3; i <= NF; i++) { # Initialize min and max for each kernel time
            vmin[machine" "i] = $i + 1000000.0;
            vmax[machine" "i] = $i + 0.0;
        }
    }
    seen[machine] = 1;

    # Assign index to unique num_threads used and build a map
    if (seen_nts[machine" "nt] == 0) {
        seen_nts[machine" "nt] = 1;
        nnts[machine] ++;  # The number of different numbers of threads used on this machine
        nts[machine" "nnts[machine]] = nt; # (machine, nts_id) -> nt
        nt_ids[machine" "nt] = nnts[machine]; # (machine, nt) -> nts_id
    }

    nt_i = nt_ids[machine" "nt];

    for (i=5; i <= NF; i++) {
        if ($i !~ /^[[:space:]]*-?[0-9]+(\.[0-9]+)?[[:space:]]*$/) { # check if numeric?
            continue
        }
        val = $i + 0.0;
        # The first case is the number of threads as many as the physical cores
        # The second is the half of that.
        vall[machine" "i" "nt] = $i

        if (val > 0.0) {
            cnt_f[machine" "i] ++;
            if (vmin[machine" "i] > val) {
                vmin[machine" "i] = val;
            }
            if (vmax[machine" "i] < val) {
                vmax[machine" "i] = val;
            }
        }
    }
}

END {
    # The numbers are already averages. We find min and max of those average
    # kernel times per machine regardless of the number of threads used
    #print "Avg_Min"
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        printf("%s%s any min%s%s", machine, OFS, OFS, OFS);
        for (i=5; i <= NF; i++) {
            c = cnt_f[machine" "i];
            if (c > 0)
                printf("%s%f", OFS, vmin[machine" "i]);
            else
                printf("%s", OFS);
        }
        printf("\n");
    }
    #print "Avg_Max"
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        printf("%s%s any max%s%s", machine, OFS, OFS, OFS);
        for (i=5; i <= NF; i++) {
            c = cnt_f[machine" "i];
            if (c > 0)
                printf("%s%f", OFS, vmax[machine" "i]);
            else
                printf("%s", OFS);
        }
        printf("\n");
    }
    #print "Avg_FullThreads"
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        nt = nts[machine" "1]
        printf("%s%s %u (full)%s%s", machine, OFS, nt, OFS, OFS);
        for (i=5; i <= NF; i++) {
            printf("%s%f", OFS, vall[machine" "i" "nt]);
        }
        printf("\n");
    }
    #print "Avg_HalfThreads"
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        nt = nts[machine" "2]
        printf("%s%s %u (half)%s%s", machine, OFS, nt, OFS, OFS);
        for (i=5; i <= NF; i++) {
            printf("%s%f", OFS, vall[machine" "i" "nt]);
        }
        printf("\n");
    }
    #print "Avg_QtrThreads"
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        nt = nts[machine" "3]
        nt_qtr = nts[machine" " 1]/4
        if (nt > nt_qtr) {
          for (k=3; k <= nnts[machine]; k++) {
            nt_k = nts[machine" "k]
            if (nt_k == nt_qtr) {
              nts[machine" "3] = nt_qtr
              nts[machine" "k] = nt
              nt_ids[machine" "nt_qtr] = 3
              nt_ids[machine" "nt] = k
              nt = nt_qtr
              break;
            }
          }
        }
        printf("%s%s %u (quarter)%s%s", machine, OFS, nt, OFS, OFS);
        for (i=5; i <= NF; i++) {
            printf("%s%f", OFS, vall[machine" "i" "nt]);
        }
        printf("\n");
    }
    for (j=1; j <= n_m; j++) {
        machine = name[j];
        ntid_32 = nt_ids[machine" "32]
        if ((ntid_32 == 0) || (ntid_32 < 4)) {
           continue
        }

        printf("%s%s %u%s%s", machine, OFS, 32, OFS, OFS);
        for (i=5; i <= NF; i++) {
            printf("%s%f", OFS, vall[machine" "i" "32]);
        }
        printf("\n");
    }
}
