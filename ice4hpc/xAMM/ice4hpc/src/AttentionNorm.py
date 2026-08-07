import torch

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

