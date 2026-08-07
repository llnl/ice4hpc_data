import re
import os
import pandas as pd

def save_embeddings(df, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved embeddings to {output_path}")

def split_by_machine(df, output_dir, machine_col='machine'):
    os.makedirs(output_dir, exist_ok=True)

    # Group similar machine labels (e.g., A1, A2 -> A.csv)
    def extract_base_label(label):
        match = re.match(r"([A-Za-z]+)", str(label))
        return match.group(1) if match else str(label)

    df['__group_label__'] = df[machine_col].apply(extract_base_label)

    for group_label, group in df.groupby('__group_label__'):
        machine_file = os.path.join(output_dir, f"{group_label}.csv")
        group.drop(columns='__group_label__').to_csv(machine_file, index=False)

    print(f"Split embeddings by base label of '{machine_col}' into {output_dir}")