import torch
import torch.nn.functional as F
import pandas as pd

# Load the CSV file into a PyTorch tensor, handling NaN values
def load_csv_to_tensor(file_path, fill_value=0):
    df = pd.read_csv(file_path)
    
    # Fill empty cells (NaN) with the specified value
    df = df.fillna(fill_value)

    # Convert the DataFrame to a PyTorch tensor
    embeddings = torch.tensor(df.values, dtype=torch.float32)
    return embeddings

# Compute attention weights based on variance
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
    print("Attention weights:", normalized_weights)
    return normalized_weights

# Apply attention weights to the embeddings
def apply_attention_weights(embeddings, attention_weights):
    # Multiply attention weights with embeddings to get the resulting weighted embeddings
    weighted_embeddings = torch.matmul(attention_weights.unsqueeze(0), embeddings)
    return weighted_embeddings

# Example usage
if __name__ == "__main__":
    # Load the embeddings from CSV
    csv_file = "machine_embedding10_machines/Quartz.csv"  # Replace with your file path
    
    # Handle NaN by filling them with a value (e.g., 0)
    embeddings = load_csv_to_tensor(csv_file, fill_value=0)

    # Compute attention weights
    attention_weights = compute_attention_weights_based_on_variance(embeddings)

    # Apply the attention weights
    weighted_result = apply_attention_weights(embeddings, attention_weights)

    print("Weighted embeddings:", weighted_result)
