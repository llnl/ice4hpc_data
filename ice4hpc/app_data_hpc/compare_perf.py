# Compare the relative performance between two runs.
# For each run in the old dataset, we find a compatible run in the new dataset,
# in terms of the matching application, the application arguments used, the
# machine used and the number of ranks used to run the job.
# In case that there is no matching machine in the new dataset, we match some
# ther machine so that we can at least get the sense of validity of result.

import pandas as pd

old_perf_file="~/generalizable_modeling/app_data_hpc/merged.txt"
new_perf_file="/usr/workspace/ice4hpc/Apps/data/merged.txt"


old_perf = pd.read_csv(old_perf_file)
new_perf = pd.read_csv(new_perf_file)

old_perf.columns = ['machine', 'ranks', 'app', 'args', 'REALTIME (sec)' ]
new_perf.columns = ['machine', 'ranks', 'app', 'args', 'REALTIME (sec)' ]

matching = {'corona': 'corona',
            'corona-cpu': 'corona-cpu',
            'lassen': 'matrix',
            'lassen-cpu': 'dane',
            'quartz': 'borax',
            'ruby': 'dane'}

matching2 = {'corona': 'mammoth',
             'corona-cpu': 'mammoth',
             'lassen': 'dane',
             'lassen-cpu': 'borax',
             'quartz': 'dane',
             'ruby': 'dane'}

for index, row in old_perf.iterrows():
    machine = row['machine']
    ranks = row['ranks']
    app = row['app']
    args = row['args']
    old_time = row['REALTIME (sec)']

    new_row = new_perf[(new_perf['args'] == args) & \
                       (new_perf['machine'] == matching[machine]) & \
                       (new_perf['app'] == app) & \
                       (new_perf['ranks'] == ranks)]
    if new_row.empty:
        new_row = new_perf[(new_perf['args'] == args) & \
                           (new_perf['machine'] == matching2[machine]) & \
                           (new_perf['app'] == app) & \
                           (new_perf['ranks'] == ranks)]
        if new_row.empty:
            print(f'{machine},{ranks},{app},"{args}",{old_time: .6f} cannot be matched')
            continue
        else:
            machine = machine + "->" + matching2[machine]
    else:
        machine = machine + "->" + matching[machine]

    new_time = new_row['REALTIME (sec)'].iloc[0]
    speedup = old_time / new_time
    print(f'{machine},{ranks},{app},"{args}",{old_time: .6f},{new_time: .6f},{speedup: .3f}')
