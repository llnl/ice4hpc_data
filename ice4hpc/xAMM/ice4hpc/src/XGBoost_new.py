from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder
import yaml
import optuna
import os
import numpy as np
import pandas as pd
import util

class CustomLabelEncoder:
    def __init__(self):
        self.label_mapping = {}
    
    def fit(self, labels):
        unique_labels = np.unique(labels)
        self.label_mapping = {label: idx for idx, label in enumerate(unique_labels)}
        self.label_mapping['unknown'] = -1  # Fallback for unseen labels
    
    def transform(self, labels):
        # Convert each label to a hashable type before looking it up
        return [
            self.label_mapping.get(label.item() if isinstance(label, np.ndarray) else label, 
                                   self.label_mapping['unknown'])
            for label in labels
        ]

class XGBoost():
    def __init__(self, num_of_estimators):
        self.num_of_estimators = int(num_of_estimators)

    def __call__(self, config_yaml, X_train, Y_train, tar_x_scaled, tar_y_scaled):
        # Load the configuration file
        with open(config_yaml, "r") as f:
            global_config = yaml.load(f, Loader=yaml.FullLoader)
        
        # Define paths from configuration
        csv_path = os.getcwd() + global_config["csv_path"]
        indices_path = os.getcwd() + global_config["indices_path"]
        folder_name = "RF"

        label_encoder = CustomLabelEncoder()
        label_encoder.fit(Y_train.reshape(-1,1))
        Y_train_encoded=label_encoder.transform(Y_train.reshape(-1,1))
        tar_y_encoded = label_encoder.transform(tar_y_scaled.reshape(-1,1))

        # Define the Optuna objective function
        def objective(trial):
            # Define the hyperparameters for GradientBoostingClassifier
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 200),
                'learning_rate': trial.suggest_loguniform('learning_rate', 0.01, 0.2),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
                'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
                'subsample': trial.suggest_uniform('subsample', 0.5, 1.0),
                'max_features': trial.suggest_uniform('max_features', 0.5, 1.0),
                # 'alpha': trial.suggest_uniform('alpha', 0.75, 0.99)
            }

            # Train the model on dataset A
            model = GradientBoostingClassifier(**params)
            model.fit(X_train, Y_train_encoded)

            # Predict on the target dataset
            predictions = model.predict(tar_x_scaled)

            # Calculate classification metrics
            accuracy = accuracy_score(tar_y_encoded, predictions)
            precision = precision_score(tar_y_encoded, predictions, average='weighted')
            recall = recall_score(tar_y_encoded, predictions, average='weighted')

            # For Optuna, we aim to maximize accuracy, so return negative accuracy
            return -accuracy

        # Create the Optuna study and optimize
        study = optuna.create_study(direction='maximize')  # For classification, maximize performance
        study.optimize(objective, n_trials=100)

        # Get the best hyperparameters from the study
        best_params = study.best_params

        # Train the final model with the best hyperparameters
        model = GradientBoostingClassifier(**best_params)
        model.fit(X_train, Y_train_encoded)

        # Evaluate the model on the target dataset
        predictions = model.predict(tar_x_scaled)
        accuracy = accuracy_score(tar_y_encoded, predictions)
        precision = precision_score(tar_y_encoded, predictions, average='weighted')
        recall = recall_score(tar_y_encoded, predictions, average='weighted')

        # Output the best parameters and performance metrics
        print(f"Best parameters obtained from Optuna: {best_params}")
        print(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}")

        # Save the scatter plot of actual vs predicted (for visualization)
        util.scatterPlot(tar_y_encoded, predictions,os.getcwd() + global_config["fig_path"] + "actual_vs_predicted_XGB.pdf","Actual_VS_Predicted (Classification)")

        cm = confusion_matrix(tar_y_encoded, predictions)
        print("Confusion Matrix:")
        print(cm)

        # Return the final evaluation metrics
        return accuracy, precision
