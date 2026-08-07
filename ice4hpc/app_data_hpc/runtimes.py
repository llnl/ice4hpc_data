# Load the performce from 4 different machines.
# The IPDPS24 paper describes that the mean average error (MAE) of the relative
# performance model is 0.11. Unfortunately, we do not have the model itself.
# Instead, we can add a zero-mean Gaussian noise to produce 11% mean absolute
# error (MAE) mimicking the prediction model behavior. For that the standard
# deviation is (sigma_scaler * run_time). So, for every run time value, need to randomly
# pick a value from the normal distribution N(0, (sigma_scaler×t)^2) to represent the
# predicted run time.
# We clean the outlier potentially due to failed jobs on corona.

import pandas as pd
import numpy as np
import math

df = pd.read_csv('runtimes.csv')

df = df.drop(columns=['no'])
print(df.head())

# Check if data has any non-numeric or zero for run time value.
non_numeric_mask = df.apply(lambda s: pd.to_numeric(s, errors='coerce').isna() & s.notna())
zero_mask = (df == 0)
bad_rows_mask = non_numeric_mask | zero_mask

if bad_rows_mask.any().any() :
    print(df[bad_rows_mask.any(axis=1)])


# Compute relative performance
new_cols = ['ruby_rp', 'lassen_rp', 'corona_rp', 'rp_max']
df = df.reindex(columns=df.columns.tolist() + new_cols)

df['ruby_rp'] = df['ruby'] / df['quartz']
df['lassen_rp'] = df['lassen'] / df['quartz']
df['corona_rp'] = df['corona'] / df['quartz']
df['rp_max'] = df[['ruby_rp','lassen_rp','corona_rp']].max(axis=1)

# Filter outlier possibly due to failures
indices_to_drop = df[(df['corona_rp'] < 0.015) | (df['corona_rp'] > 10)].index
df.loc[indices_to_drop].to_csv('dropped.csv', index=False)
df = df.drop(index=indices_to_drop)
num_to_drop = len(indices_to_drop)
print(f"Number of samples dropped: {num_to_drop}")
print("Number of samples kept: ", df.shape[0])

# Compute statistics
summary_stats = df.agg(['mean', 'min', 'max', 'std'])
print("Summary statistics:\n", summary_stats)

# Check the extreme cases for sanity
top_idx = df['rp_max'].nlargest(100, keep='all').index
bottom_idx = df['rp_max'].nsmallest(100, keep='all').index
extreme_idx = top_idx.union(bottom_idx)
#df_outliers = pd.concat([df.loc[extreme_idx], df.loc[extreme_idx]], axis=1)
df_outliers = df.loc[extreme_idx]
print(df_outliers)
df_outliers.sort_values('rp_max', ascending=True).to_csv('outliers.csv', index=False)

# Add columns for predicted run times and predicted relative performances
pred_cols = ['quartz_p', 'ruby_p', 'lassen_p', 'corona_p', 'ruby_prp', 'lassen_prp', 'corona_prp']
df = df.reindex(columns=df.columns.tolist() + pred_cols)

# Prepare to compute white noise to represent prediction error of execution time model
seed_pred = 1139
rng = np.random.default_rng(seed=seed_pred)
mae_targeted = 0.077 # mae of run time prediction is calibrated to match MAE 0.11 for the relative performance
sigma_scaler = mae_targeted * math.sqrt(math.pi / 2)

# The prediction error mimicked
df_err = pd.DataFrame(index=df.index, columns=['quartz', 'ruby', 'lassen', 'corona', 'ruby_prp', 'lassen_prp', 'corona_prp'])

machines = ['quartz', 'ruby', 'lassen', 'corona']

# Generate prediction error.
# If error is negative and its magnitude is bigger than the original regenerate
for col in ['quartz', 'ruby', 'lassen', 'corona'] :
    df_err[col] = rng.normal(loc=0, scale = sigma_scaler * df[col])
    mask = (df[col] < -df_err[col])

    iteration = 0
    while mask.any():
        iteration += 1
        failed_count = mask.sum()
        print(f"Column '{col}' | Iteration {iteration}: Regenerating {failed_count} rows...")

        # Only pick the indices where the condition failed
        failed_indices = mask[mask].index
    
        # Regenerate noise for ONLY those indices
        new_noise = rng.normal(loc=0, scale = sigma_scaler * df.loc[failed_indices, col])
    
        # Update the error column
        df_err.loc[failed_indices, col] = new_noise
    
        # Re-check the mask
        mask = (df[col] < -df_err[col])

    print(f"Column '{col}' finalized after {iteration} regenerations.")



# Represent prediction error of execution time model
df['quartz_p'] = df['quartz'] + df_err['quartz']
df['ruby_p'] = df['ruby'] + df_err['ruby']
df['lassen_p'] = df['lassen'] + df_err['lassen']
df['corona_p'] = df['corona'] + df_err['corona']

# Compute predicted relative performances and print statistics
df['ruby_prp'] = df['ruby_p'] / df['quartz_p']
df['lassen_prp'] = df['lassen_p'] / df['quartz_p']
df['corona_prp'] = df['corona_p'] / df['quartz_p']
df.to_csv('scheduling_samples.csv', index=False)

prp_stats = df[['ruby_prp', 'lassen_prp', 'corona_prp']].agg(['mean', 'min', 'max', 'std'])
print("Statistics of predicted relative performance:\n", prp_stats)

# Analysis of the error generated
df_err['quartz'] = (df['quartz_p']/df['quartz']-1).abs()
df_err['ruby'] = (df['ruby_p']/df['ruby']-1).abs()
df_err['lassen'] = (df['lassen_p']/df['lassen']-1).abs()
df_err['corona'] = (df['corona_p']/df['corona']-1).abs()
df_err['ruby_prp'] = (df['ruby_prp']/df['ruby_rp'] - 1).abs()
df_err['lassen_prp'] = (df['lassen_prp']/df['lassen_rp'] - 1).abs()
df_err['corona_prp'] = (df['corona_prp']/df['corona_rp'] - 1).abs()

err_stats = df_err.agg(['mean', 'min', 'max', 'std'])
print("Prediction error statistics:\n", err_stats)

