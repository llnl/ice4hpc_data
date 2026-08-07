import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

def compute_attention_weights(embedding, temperature=1.0):
    # Step 1: Compute the L2 norm of each embedding
    scores = torch.norm(embedding, dim=1)
    print("L2 Norm Scores:", scores)

    # Step 2: Apply Leaky ReLU activation
    scores = F.leaky_relu(scores, negative_slope=0.01)
    print("Leaky ReLU Scores:", scores)

    # Step 3: Apply logarithm transformation
    scores = torch.log1p(scores)
    print("Log1p Scores:", scores)

    # Step 4: Normalize by temperature
    scores = scores / temperature
    print("Normalized Scores:", scores)

    # Step 5: Subtract the maximum score for numerical stability
    scores -= torch.max(scores)
    print("Scores after Subtracting Max:", scores)

    # Step 6: Compute softmax to obtain attention weights
    normalized_weights = torch.softmax(scores, dim=0)
    return normalized_weights

def apply_attention_weights(embeddings, attention_weights):
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
attention_weights = compute_attention_weights(embeddings_tensor)

# Apply attention weights to get the resulting 1x2 matrix
weighted_embeddings = apply_attention_weights(embeddings_tensor, attention_weights)

# Convert weighted embeddings to numpy array for easier viewing
weighted_embeddings_numpy = weighted_embeddings.numpy()

print("Attention Weights:", attention_weights.shape)
print(f"Weighted Embeddings: {weighted_embeddings_numpy.shape}")
weighted_embeddings_numpy_df = pd.DataFrame(weighted_embeddings_numpy)
# print(weighted_embeddings_numpy.shape)
weighted_embeddings_numpy_df.to_csv('weighted_embeddings_Corona.csv', index=False)