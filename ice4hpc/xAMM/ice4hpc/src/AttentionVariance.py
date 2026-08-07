import torch

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
