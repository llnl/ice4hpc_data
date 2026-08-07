import numpy as np
import torch
import torch.nn.functional as F
import pandas as pd

def compute_attention_weights_based_on_variance(embedding, temperature=1.0):
    # Step 1: Calculate the variance for each embedding
    variances = torch.var(embedding, dim=1)

    # Step 2: Apply Leaky ReLU activation
    variances = F.leaky_relu(variances, negative_slope=0.01)

    # Step 3: Apply logarithm transformation
    variances = torch.log1p(variances)

    # Step 4: Normalize by temperature
    variances = variances / temperature

    # Step 5: Subtract the maximum variance for numerical stability
    variances -= torch.max(variances)

    # Step 6: Compute softmax to obtain attention weights
    normalized_weights = torch.softmax(variances, dim=0)
    print(normalized_weights)
    return normalized_weights

def apply_attention_weights1(embeddings, attention_weights):
    # Multiply attention weights with embeddings to get the resulting 1x2 matrix
    weighted_embeddings = torch.matmul(attention_weights.unsqueeze(0), embeddings)
    return weighted_embeddings

# Load sample data
file_path = 'Corona.csv'
embeddings = pd.read_csv(file_path)

# Check for NaN values in the DataFrame
print("Data contains NaN values: ", embeddings.isnull().values.any())

# Fill NaN values with the mean of each column after removing the first column
embeddings_filled = embeddings.iloc[:, 1:].fillna(embeddings.iloc[:, 1:].mean())

# Convert the filled DataFrame to a numpy array
embeddings_array = embeddings_filled.values
print("Embeddings array after filling NaNs:", embeddings_array.shape)

# Convert embeddings to a tensor
embeddings_tensor = torch.tensor(embeddings_array, dtype=torch.float)

# Ensure no NaN or infinite values in the tensor
if torch.isnan(embeddings_tensor).any() or torch.isinf(embeddings_tensor).any():
    print("Embedding tensor contains NaN or infinite values.")

# Compute attention weights
attention_weights = compute_attention_weights_based_on_variance(embeddings_tensor)
print(f'embeddings_tensor {embeddings_tensor.shape}')

# Apply attention weights to get the resulting 1x2 matrix
variance_embeddings = apply_attention_weights1(embeddings_tensor, attention_weights)

# Convert weighted embeddings to numpy array for easier viewing
variance_embeddings_numpy = variance_embeddings.numpy()

print("Attention Weights:", attention_weights.shape)
print("Variance Embeddings:")
variance_embeddings_numpy_df = pd.DataFrame(variance_embeddings_numpy)
print(variance_embeddings_numpy.shape)
variance_embeddings_numpy_df.to_csv('variance_embeddings_Corona.csv', index=False)