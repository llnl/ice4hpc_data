import pandas as pd
import torch
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import DataLoader, TensorDataset
from tab_network import TabNetPretraining

def generate_embeddings(file_path, cat_columns, emb_dims, target_column, id_column='machine'):
    print(f"Processing: {file_path}")

    # Load and fill NA with 0 (like the original script)
    df = pd.read_csv(file_path)
    df = df.fillna(0)
    id_values = df[id_column].copy()

    # Encode categorical columns
    label_encoders = {col: LabelEncoder() for col in cat_columns}
    for col in cat_columns:
        df[col] = label_encoders[col].fit_transform(df[col])

    # Drop target column
    X = df.drop([target_column], axis=1, errors='ignore')
    X_tensor = torch.tensor(X.values, dtype=torch.float32)

    # Embedding setup
    cat_dims = [len(label_encoders[col].classes_) for col in cat_columns]
    cat_idxs = [X.columns.get_loc(col) for col in cat_columns]
    cat_emb_dims = emb_dims
    input_dim = X.shape[1]
    group_matrix = torch.eye(input_dim)

    # Model
    model = TabNetPretraining(
        input_dim=input_dim,
        pretraining_ratio=0.2,
        n_d=8,
        n_a=8,
        n_steps=3,
        gamma=1.3,
        cat_idxs=cat_idxs,
        cat_dims=cat_dims,
        cat_emb_dim=cat_emb_dims,
        virtual_batch_size=128,
        mask_type="entmax",
        group_attention_matrix=group_matrix
    )

    # Train
    loader = DataLoader(TensorDataset(X_tensor), batch_size=256, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = torch.nn.MSELoss()
    model.train()

    for epoch in range(20):
        total_loss = 0
        for (x_batch,) in loader:
            x_batch = torch.nan_to_num(x_batch, nan=0.0)
            reconstructed, original, _ = model(x_batch)
            loss = loss_fn(reconstructed, original)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * x_batch.size(0)
        print(f"Epoch {epoch + 1}: Loss = {total_loss / len(loader.dataset):.6f}")

    # Inference
    model.eval()
    with torch.no_grad():
        embeddings = model.embedder(X_tensor)
        embeddings_df = pd.DataFrame(embeddings.numpy())
        embeddings_df.insert(0, id_column, id_values.values)

        # Add target column back
        if target_column in df.columns:
            target_values = df[target_column].values
            embeddings_df[target_column] = target_values

    return embeddings_df
