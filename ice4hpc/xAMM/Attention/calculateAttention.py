import pandas as pd
import torch
import torch.nn.functional as F

def compute_attention_weights(embedding, temperature=1.0):
    scores = torch.norm(embedding, dim=1)
    scores = F.leaky_relu(scores, negative_slope=0.01)
    scores = torch.log1p(scores)
    scores = scores / temperature
    scores -= torch.max(scores)
    normalized_weights = torch.softmax(scores, dim=0)
    return normalized_weights

def apply_attention_and_convert_to_tensor(df):
    embeddings_tensor = torch.tensor(df.values, dtype=torch.float)
    attention_weights = compute_attention_weights(embeddings_tensor)
    attention_weights_expanded = attention_weights.unsqueeze(1).expand_as(embeddings_tensor)
    weighted_embeddings = attention_weights_expanded * embeddings_tensor
    return weighted_embeddings

def clean_and_convert_to_numeric(df, exclude_columns=[]):
    for col in df.columns:
        if col not in exclude_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.fillna(0, inplace=True)
    return df

# Load CSV file
df = pd.read_csv('../MachineData/Normalized_separated_embeddings_10/Quartz.csv')

# Clean the dataframe
df_cleaned = clean_and_convert_to_numeric(df, exclude_columns=['machine', 'machine1'])

# Apply attention weights to the remaining features
weighted_embeddings = apply_attention_and_convert_to_tensor(df_cleaned)
weighted_features_df = pd.DataFrame(weighted_embeddings.numpy(), columns=df_cleaned.columns)

# Save the final DataFrame with weighted features
weighted_features_df.to_csv('../MachineData/Attention_embeddings_and_Normalized/NormalizedQuartzWithAttention.csv', index=False)