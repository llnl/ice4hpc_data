import pandas as pd

# Load the first CSV (multiple rows)
df1 = pd.read_csv("Application_embeddings.csv", header=None)

# Load the second CSV (values to append to every row)
df2 = pd.read_csv("Machine.csv", header=None)

# Get the first row of df2 as a list (we assume df2 has just one row)
values_to_append = df2.iloc[0].tolist()

# Repeat the row from df2 to match the number of rows in df1
df2_repeated = pd.DataFrame([values_to_append] * len(df1))

# Concatenate the two dataframes column-wise
result = pd.concat([df1, df2_repeated], axis=1)

# Save the result to a new CSV
result.to_csv("combined.csv", index=False, header=False)
