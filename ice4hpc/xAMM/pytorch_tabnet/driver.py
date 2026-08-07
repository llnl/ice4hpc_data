import yaml
from embedding_utils import generate_embeddings
from file_utils import save_embeddings, split_by_machine

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()

    # Generate machine embeddings
    machine_emb_df = generate_embeddings(
        file_path=config['machine_data_path'],
        cat_columns=config['machine_dataset_categorical_columns'],
        emb_dims=config['machine_embedding_dim'],
        target_column=config['target_column'],
        id_column='machine'
    )
    save_embeddings(machine_emb_df, config['machine_output_path'])
    split_by_machine(machine_emb_df, config['split_machine_output_dir'], machine_col='machine')

    # Generate app embeddings
    # app_emb_df = generate_embeddings(
    #     file_path=config['app_data_path'],
    #     cat_columns=config['application_dataset_categorical_columns'],
    #     emb_dims=config['app_embedding_dim'],
    #     target_column=config['target_column'],
    #     id_column='app'
    # )
    # save_embeddings(app_emb_df, config['app_output_path'])
if __name__ == '__main__':
    main()
