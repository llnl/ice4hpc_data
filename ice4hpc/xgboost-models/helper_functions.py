import pandas as pd
import matplotlib.pyplot as plt
import textwrap
import numpy as np
import math

from xgboost import XGBRegressor
import xgboost as xgb

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedKFold
from sklearn.metrics import make_scorer
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

#define custom function which returns single output as metric score
def NMAPE(y_true, y_pred): 
    return (1 - np.mean(np.abs((y_true - y_pred) / y_true))) * 100

#make scorer from custome function
nmape_scorer = make_scorer(NMAPE)

def wrap_labels(ax, width, break_long_words=False, rot=0):
    labels = []
    for label in ax.get_xticklabels():
        text = label.get_text()
        labels.append(textwrap.fill(text, width=width,
                      break_long_words=break_long_words))
    ax.set_xticklabels(labels, rotation=rot)

def get_data() -> pd.DataFrame:
    data_df = pd.read_csv('../app_data_hpc/ds_train.csv')
    data_df = data_df.dropna(subset=['REALTIME (sec)'])
    return data_df

def show_data_summary(data_df, machine_col='machine'):
    apps = data_df['app'].unique()
    machines = data_df[machine_col].unique()
    label_num_samples_per_mach = []
    num_samples_per_mach = []
    
    df_rows, df_cols = data_df.shape
    print('Num samples = ', df_rows)
    print('Num columns = ', df_cols)
    print('\n---------------------------------------------')
    print('Num apps = ', len(apps))
    for app in apps:
        print('    - ', app, len(data_df[data_df['app'] == app]))
    print('\n---------------------------------------------')
    print('Num machines = ', len(machines))
    for machine in machines:
        num_msamples = len(data_df[data_df[machine_col] == machine])
        label_num_samples_per_mach.append(machine)
        num_samples_per_mach.append(num_msamples)
        print('    - ', machine, num_msamples)
    print('---------------------------------------------')
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', 0)
    print('\n---------------------sample 1------------------\n', data_df.iloc[0,:])
    print('\n---------------------sample 2------------------\n', data_df.iloc[1,:])
    return (label_num_samples_per_mach, num_samples_per_mach)
    
# function to add value labels
def addlabels(x,y):
    for i in range(len(x)):
        plt.text(i,y[i],y[i])

def set_plt_size():
    BIGGER_SIZE = 16
    plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=BIGGER_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure titleplt.pyplot.show()
    # plt.rcParams["figure.figsize"] = (20,10)

# To be able to calculate the relative performance, there need to be samples collected
# by running the same app with the same args using the same ranks on multiple platforms.
# If it has run only on one platform, we cannot calculate the relative performance
def drop_unmatched_rows(data_df: pd.DataFrame) -> pd.DataFrame:
    all_machines = data_df['machine'].unique()
    num_no_match = 0
    no_match_rows = []
    for index, row in data_df.iterrows():
        row_args = row['args']
        row_ranks = row['ranks']
        # assert that this run is available in all machines
        row_is_common = False
        comp_row = data_df.loc[data_df['args'] == row_args].loc[data_df['ranks'] == row_ranks]
        if len(comp_row) < 2:
            num_no_match += 1
            no_match_rows.append(index)
    # drop the rows with no matches
    return data_df.drop(index=no_match_rows)


# for each args, ranks combo, we want to
# 1. make combinations of base machine and target machine available
# 2. for each combination, calculate the relative performance
# We know that for N machines, there are N*N=N^2 combinations
def create_machine_combinations(data_df: pd.DataFrame) -> pd.DataFrame:
    new_data_df: pd.DataFrame = None
    all_args = data_df.args.unique()
    for args in all_args:
        filtered_by_args = data_df[data_df.args == args]
        all_ranks = filtered_by_args.ranks.unique()
        for ranks in all_ranks:
            filtered_by_ranks_and_args = filtered_by_args[filtered_by_args.ranks == ranks]
            all_machines = filtered_by_ranks_and_args['source machine'].unique()
            for source_machine in all_machines:
                # print('num all machines', len(all_machines))
                temp_df = filtered_by_ranks_and_args[filtered_by_ranks_and_args['source machine'] == source_machine].copy(deep=True)
                base_df = temp_df.copy(deep=True)
                # replicating the perf counter features of the source machine
                # as many as the number of target machines.
                # we don't need the perf counter features of the target machine.
                # We make placeholder lines for machine characterization features.
                for i in range (1, len(all_machines)):
                    temp_df = pd.concat([temp_df, base_df.copy(deep=True)])
                temp_df['target machine'] = all_machines.copy()
                new_data_df = pd.concat([new_data_df, temp_df])
    return new_data_df

def merge_benchmarks(data_df: pd.DataFrame, merge_on_ranks: bool = False) -> pd.DataFrame:
    # file_cpu = '../raja-data/omp-c-rep0.5-sz2.0.txt'
    # file_gpu = '../raja-data/gpu-rep0.5-sz2.0.txt'
    # raja_df = pd.read_csv(file_cpu)
    # raja_df_gpu = pd.read_csv(file_gpu)
    # # filter to only averages
    # raja_df = raja_df.loc[raja_df['Kernel                      '].isna()]
    # raja_df = raja_df.loc[~raja_df['machine'].str.startswith('AVERAGE')]
    # raja_df = raja_df.drop(columns=['Kernel                      .1', 'Kernel                      '])    
    # raja_df.machine[raja_df['machine'] == 'ec2-c5n'] = 'ec2-c5.metal'
    # raja_df.machine[raja_df['machine'] == 'ec2-c6i'] = 'ec2-c6i.metal'

    # raja_df_gpu = raja_df_gpu.loc[raja_df_gpu['Kernel                      '].isna()]
    # raja_df_gpu = raja_df_gpu.loc[~raja_df_gpu['machine'].str.startswith('AVERAGE')]
    # raja_df_gpu = raja_df_gpu.drop(columns=['Kernel                      .1', 'Kernel                      '])
    # # raja_df = pd.concat([raja_df, raja_gpu_df])
    
    # raja_df = pd.concat([raja_df, raja_df_gpu])

    file = '../raja-data/all-avg-rep0.5-sz2.0.txt'
    raja_df = pd.read_csv(file)

    raja_df.loc[raja_df['machine'] == 'ec2-c5n', 'machine'] = 'ec2-c5.metal'
    raja_df.loc[raja_df['machine'] == 'ec2-c6i', 'machine'] = 'ec2-c6i.metal'
    # raja_df.dropna(axis=1,how='all',inplace=True)
    raja_df = raja_df.drop(columns=['Kernel                      .1', 'Kernel                      '])    
    raja_df = raja_df.rename(columns={'core': 'ranks'})

    if not merge_on_ranks:
        raja_df = raja_df[raja_df['ranks'] == 1]
        raja_df = raja_df.drop(columns=['ranks'])

    raja_source = raja_df.add_prefix('source ')
    raja_target = raja_df.add_prefix('target ')
    # print(raja_source.columns)
    if merge_on_ranks:
        raja_source = raja_source.rename(columns={'source ranks': 'ranks'})
        raja_target = raja_target.rename(columns={'target ranks': 'ranks'})
        data_df = data_df.merge(raja_source, on=['source machine', 'ranks'])
        data_df = data_df.merge(raja_target, on=['target machine', 'ranks'])
    else:
        data_df = data_df.merge(raja_source, on=['source machine'])
        data_df = data_df.merge(raja_target, on=['target machine'])
    
    return data_df

def calc_relative_performances(data_df: pd.DataFrame) -> pd.DataFrame:
    rel_perf_list = []
    target_sid = []
    #with open('source_target_speedup.txt', 'w') as f:
    for index, row in data_df.iterrows():
        # print(row)
        base_performance = row['REALTIME (sec)']
        row_args = row['args']
        row_ranks = row['ranks']
        source_machine = row['source machine']
        target_machine = row['target machine']

        comp_row = data_df[(data_df['args'] == row_args) \
                 & (data_df['source machine'] == target_machine) \
                 & (data_df['target machine'] == source_machine) \
                 &  (data_df['ranks'] == row_ranks)]

        target_performance = comp_row['REALTIME (sec)'].iloc[0]
        relative_performance = base_performance/target_performance
        #relative_performance = target_performance/base_performance
        rel_perf_list.append(relative_performance)
        target_sid.append(comp_row['sid'].iloc[0])

    data_df['relative performance'] = rel_perf_list
    data_df['target_sid'] = target_sid;
    '''
    with open('source_target_speedup.txt', 'w') as f:
        for index, row in data_df.iterrows():
          row_args = row['args']
          row_ranks = row['ranks']
          source_machine = row['source machine']
          target_machine = row['target machine']

          comp_row = data_df[(data_df['args'] == row_args) \
                & (data_df['source machine'] == target_machine) \
                & (data_df['target machine'] == source_machine) \
                &  (data_df['ranks'] == row_ranks)]

          if not math.isclose(row['relative performance'] * comp_row['relative performance'], 1.0, rel_tol=1e-9) :
              print(f"{source_machine}, {target_machine}, \
                      {row['sid']}, {comp_row['sid']}, \
                      {row['relative_performance']}, {comp_row['relative performance']}", \
                      file = f)
    '''
    return data_df

def remove_unneeded_columns(data_df: pd.DataFrame) -> pd.DataFrame:
    refined_df = data_df.drop(columns=['app', 'args', 'target machine', 'source machine', 'duration', 'Overhead', 'sid', 'target_sid'])
    # data_df = data_df.drop(columns=['machine',  'app', 'exec', 'args', 'modules', 'spack_env', 'exec_path', 'events', 'path', 'duration'])
    refined_df = refined_df.fillna(0.0)
    return refined_df

def split_x_y(refined_df: pd.DataFrame) -> (np.ndarray, np.ndarray):
    run_data = refined_df.drop(columns='relative performance').to_numpy()
    relative_performance_values = refined_df['relative performance'].to_numpy()
    return (run_data, relative_performance_values)

def tune_n_estimators(x_all, y_all, start_n_estimators, end_n_estimators):
    min_mean_mape = 30000
    n_estimator = 0
    num_same = 0
    for num in range(start_n_estimators, end_n_estimators, 50):
        if(num_same > 3):
            break

        model = XGBRegressor(n_estimators=num, max_depth=3)
        
        # define model evaluation method
        cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
        # evaluate model
        scores = cross_val_score(model, x_all, y_all, scoring=nmape_scorer, cv=cv, n_jobs=-1)
        # scores_mape = cross_val_score(model, x_all, y_all, scoring=mape_scorer, cv=cv, n_jobs=-1)

        # force scores to be positive
        scores = np.absolute(scores)
        # scores_mape = np.absolute(scores_mape)
        mean_mape = np.mean(scores)
        if min_mean_mape == mean_mape:
            num_same += 1
        else:
            if mean_mape < min_mean_mape:
                min_mean_mape = mean_mape
                n_estimator = num
            num_same = 0

        print('Mean MAE: %.3f (std-dev: %.3f) (n_estimators: %d)' % (scores.mean(), scores.std(), num) )
        # print('Mean MAPE: %.3f (std-dev: %.3f)' % (scores_mape.mean(), scores_mape.std()) )


    return (n_estimator, min_mean_mape)

def tune_depth(x_all, y_all, n_estimators, start_depth, end_depth):
    min_mean_mae = 1000
    max_depth = 0
    num_same = 0
    for num in range(start_depth, end_depth+1):
        if(num_same > 3):
            break

        model = XGBRegressor(n_estimators=n_estimators, max_depth=num)
        
        # define model evaluation method
        cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
        # evaluate model
        
        scores = cross_val_score(model, x_all, y_all, scoring=get_mape_scorer(), cv=cv, n_jobs=-1)
        # scores_mape = cross_val_score(model, x_all, y_all, scoring=mape_scorer, cv=cv, n_jobs=-1)

        # force scores to be positive
        scores = np.absolute(scores)
        # scores_mape = np.absolute(scores_mape)
        mean_mae = np.mean(scores)
        if min_mean_mae == mean_mae:
            num_same += 1
        else:
            if mean_mae < min_mean_mae:
                min_mean_mae = mean_mae
                max_depth = num
            num_same = 0

        print('Mean MAE: %.3f (std-dev: %.3f) (max_depth: %d)' % (scores.mean(), scores.std(), num) )
        # print('Mean MAPE: %.3f (std-dev: %.3f)' % (scores_mape.mean(), scores_mape.std()) )


    return (max_depth, min_mean_mae)


# def tune_depth(x_all, y_all, n_estimators):
#     min_mae = 1000
#     best_depth = 0
#     num_same = 0

#     for depth in range(5,11):
#         model = XGBRegressor(n_estimators=n_estimators, max_depth=depth)
#         # define model evaluation method
#         cv = RepeatedKFold(n_splits=10, n_repeats=3, random_state=1)
#         # evaluate model
#         scores = cross_val_score(model, x_all, y_all, scoring='neg_mean_absolute_error', cv=cv, n_jobs=-1)

#         # force scores to be positive
#         scores = np.absolute(scores)


#         if min_mae == scores:
#             num_same += 1
#         else:
#             if scores < min_mae:
#                 min_mae = scores
#                 best_depth = depth
#             num_same = 0

#         print('Mean MAE: %.3f (std-dev: %.3f) (max_depth: %d)' % (scores.mean(), scores.std(), depth) )
    
#     return (best_depth, min_mae)

def MAPE(y_true, y_pred): 
    mapes = np.abs((y_true - y_pred) / y_true) * 100
    return mapes
    # avg_mape = np.mean(mapes)
    # std_mape = np.std(mapes)
    # return (avg_mape, std_mape)
    #make scorer from custome function

def get_mape_scorer():
    return make_scorer(MAPE)

def test_one_app_removed(data_df: pd.DataFrame, app_name: str, model):
    app_removed = app_name
    df_minus = data_df.loc[data_df['app'] != app_removed]
    one_app = data_df.loc[data_df['app'] == app_removed]

    df_minus = remove_unneeded_columns(df_minus)
    one_app = remove_unneeded_columns(one_app)

    x_train = df_minus.drop(columns='relative performance').to_numpy()
    x_test = one_app.drop(columns='relative performance').to_numpy()

    y_train = df_minus['relative performance'].to_numpy()
    y_test = one_app['relative performance'].to_numpy()
    
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)

    mape_val = mean_absolute_percentage_error(y_test, y_pred, multioutput='raw_values')
    mse_val = mean_squared_error(y_test, y_pred, multioutput='raw_values')
    mae_val = mean_absolute_error(y_test, y_pred, multioutput='raw_values')

    return (mape_val, mse_val, mae_val)

def test_any_app_removed(data_df: pd.DataFrame, n_estimators, max_depth, eval_metric="rmse"):
    apps = data_df['app'].unique()
    mapes = []
    mses = []
    maes = []
    for app in apps:
        model = XGBRegressor(n_estimators=n_estimators, max_depth=max_depth, eval_metric=eval_metric)
        mape_val, mse_val, mae_val = test_one_app_removed(data_df, app, model)
        print('%s mape (avg, std): %.3f %.3f' % (app, np.mean(mape_val), np.std(mape_val)))
        mapes.append(mape_val)
        mses.append(mse_val)
        maes.append(mae_val)
    print('mean mape (avg, std, min, max): %.3f %.3f %.3f %.3f' % (np.mean(mapes), np.std(mapes), np.min(mapes), np.max(mapes)))
    print('mean mse (avg, std, min, max): %.3f %.3f %.3f %.3f' % (np.mean(mses), np.std(mses), np.min(mses), np.max(mses)))
    print('mean mae: (avg, std, min, max): %.3f %.3f %.3f %.3f' % (np.mean(maes), np.std(maes), np.min(maes), np.max(maes)))
    
    return (apps, mapes, maes)

def test_args_removed_helper(data_df: pd.DataFrame, args, model):
    df_minus = data_df.loc[~ data_df['args'].isin(args)]
    df_args = data_df.loc[data_df['args'].isin(args)]

    print('Num test samples: ', len(df_minus))
    print('Num train samples: ', len(df_args))

    df_minus = remove_unneeded_columns(df_minus)
    df_args = remove_unneeded_columns(df_args)

    x_train = df_minus.drop(columns='relative performance').to_numpy()
    x_test = df_args.drop(columns='relative performance').to_numpy()

    y_train = df_minus['relative performance'].to_numpy()
    y_test = df_args['relative performance'].to_numpy()
    
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    
    mape_val = mean_absolute_percentage_error(y_test, y_pred, multioutput='raw_values')
    mse_val = mean_squared_error(y_test, y_pred, multioutput='raw_values')
    mae_val = mean_absolute_error(y_test, y_pred, multioutput='raw_values')

    return (mape_val, mse_val, mae_val)

def test_args_removed(data_df: pd.DataFrame, n_estimators, max_depth):
    # first we try to split the args as evenly as possible

    args: [] = data_df['args'].unique().tolist()
    arg_sizes = []
    for arg in args:
        arg_sizes.append(len(data_df.loc[data_df['args'] == arg]))

    assert len(args) == len(arg_sizes)

    print('there are', len(args), 'total args')
    # num_args_per_split = int(math.ceil(len(data_df) * 0.2))
    num_splits = 5
    split_list = [None] * num_splits
    split_list_sizes = [0] * num_splits

    while len(args) > 0:
        max_arg_size = max(arg_sizes)
        arg_index = arg_sizes.index(max_arg_size)
        arg = args.pop(arg_index)
        arg_sizes.pop(arg_index)
        # print('arg init', arg)
        
        min_split_index = split_list_sizes.index(min(split_list_sizes))
        # print(len(split_list), len(split_list_sizes), min_split_index)
        if split_list[min_split_index] is None:
            split_list[min_split_index] = []
        (split_list[min_split_index]).append(arg)
        split_list_sizes[min_split_index] += max_arg_size
    print('split sizes', split_list_sizes)
    for arg_list in split_list:
        print('args length of', len(arg_list))
    # return None

    mapes = []
    mses = []
    maes = []
    i = 0
    for args_list in split_list:
        print('arg passed length', len(args_list))
        model = XGBRegressor(n_estimators=n_estimators, max_depth=max_depth)
        mape_val, mse_val, mae_val = test_args_removed_helper(data_df, args_list, model)
        print(i, 'of', len(split_list), 'has mape', mape_val)
        mapes.append(mape_val)
        mses.append(mse_val)
        maes.append(mae_val)
        i += 1
    
    return mapes, maes
    
def do_all_setup() -> pd.DataFrame:
    data_df = get_data()
    data_df = drop_unmatched_rows(data_df)
    data_df = data_df.loc[data_df['app'] != 'sw4lite']
    data_df = data_df.rename(columns={'machine': 'source machine'})
    data_df = create_machine_combinations(data_df)
    data_df = merge_benchmarks(data_df)
    data_df = calc_relative_performances(data_df)
    data_df = remove_unneeded_columns(data_df)
    return data_df

def split_x_y(data_df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    run_data = data_df.drop(columns='relative performance')
    relative_performance_values = data_df['relative performance']
    return (run_data, relative_performance_values)

