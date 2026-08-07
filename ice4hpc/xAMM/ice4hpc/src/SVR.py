import yaml
import optuna
import numpy as np
import os
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
import util

class SVR():
    def __init__(self, num_of_estimators):
        self.num_of_estimators = int(num_of_estimators)
    
    def __call__(self, config_yaml, X_train, Y_train, tar_x_scaled, tar_y_scaled):
        # Load configuration
        with open(config_yaml, "r") as f:
            global_config = yaml.load(f, Loader=yaml.FullLoader)
        csv_path = os.getcwd() + global_config["csv_path"]
        indices_path = os.getcwd() + global_config["indices_path"]
        folder_name = "SVC"

        # Impute missing values
        imputer = SimpleImputer(strategy='mean')
        X_train = imputer.fit_transform(X_train)
        tar_x_scaled = imputer.transform(tar_x_scaled)

        # Encode target variables
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        Y_train_encoded = encoder.fit_transform(Y_train)
        tar_y_encoded = encoder.transform(tar_y_scaled)

        # Define the Optuna objective function
        def objective(trial):
            # Define hyperparameters for LinearSVC
            params = {
                'C': trial.suggest_loguniform('C', 1e-3, 10),
                'max_iter': trial.suggest_int('max_iter', 1000, 10000)
            }

            # Train the model
            model = LinearSVC(**params)
            model.fit(X_train, np.argmax(Y_train_encoded, axis=1))  # Use class indices for training

            # Predict on target dataset
            predictions = model.predict(tar_x_scaled)
            accuracy = accuracy_score(np.argmax(tar_y_encoded, axis=1), predictions)

            # Optuna maximizes the objective, so return accuracy
            return accuracy

        # Create an Optuna study
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=100)

        # Get the best hyperparameters
        best_params = study.best_params
        print(f"Best parameters from Optuna: {best_params}")

        # Train the final model with the best hyperparameters
        model = LinearSVC(**best_params)
        model.fit(X_train, np.argmax(Y_train_encoded, axis=1))

        # Predict on the target dataset
        predictions = model.predict(tar_x_scaled)
        predicted_classes = predictions
        tar_y_classes = np.argmax(tar_y_encoded, axis=1)

        # Calculate metrics
        accuracy = accuracy_score(tar_y_classes, predicted_classes)
        precision = precision_score(tar_y_classes, predicted_classes, average='weighted')
        recall = recall_score(tar_y_classes, predicted_classes, average='weighted')

        # Print metrics
        print(f"Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")

        # Confusion Matrix
        conf_matrix = confusion_matrix(tar_y_classes, predicted_classes)
        print("Confusion Matrix:")
        print(conf_matrix)

        return accuracy
