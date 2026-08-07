import optuna
from sklearn.ensemble import BaggingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
import yaml
import os
import numpy as np
import pandas as pd

class Bagging():
    def __init__(self, num_of_estimators):
        self.num_of_estimators = int(num_of_estimators)
    
    def __call__(self, config_yaml, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, B_X_train, B_Y_train, B_tar_x_scaled, B_tar_y_scaled):
        with open(config_yaml, "r") as f:
            global_config = yaml.load(f, Loader=yaml.FullLoader)
        
        csv_path = os.getcwd() + global_config["csv_path"]
        indices_path = os.getcwd() + global_config["indices_path"]

        # Preprocessing for dataset A
        imputer_A = SimpleImputer(strategy='mean')
        A_X_train = imputer_A.fit_transform(A_X_train)
        A_tar_x_scaled = imputer_A.transform(A_tar_x_scaled)

        # Preprocessing for dataset B
        B_X_train_df = pd.DataFrame(B_X_train)
        B_tar_x_scaled_df = pd.DataFrame(B_tar_x_scaled)
        B_X_train_df, B_tar_x_scaled_df = B_X_train_df.align(B_tar_x_scaled_df, join='outer', axis=1)
        B_X_train_df = B_X_train_df.fillna(np.nan)
        B_tar_x_scaled_df = B_tar_x_scaled_df.fillna(np.nan)

        B_X_train = B_X_train_df.values
        B_tar_x_scaled = B_tar_x_scaled_df.values
        B_combined = np.vstack((B_X_train, B_tar_x_scaled))
        imputer_B = SimpleImputer(strategy='mean')
        B_combined_imputed = imputer_B.fit_transform(B_combined)
        B_X_train = B_combined_imputed[:B_X_train.shape[0], :]
        B_tar_x_scaled = B_combined_imputed[B_X_train.shape[0]:, :]

        # Define the objective function for Optuna
        def objective(trial):
            params = {
                'n_estimators': trial.suggest_categorical('n_estimators', [10, 30, 50, 100, 150, 200]),
                # 'max_features': trial.suggest_uniform('max_features', 0.5, 10),
                'max_features': trial.suggest_uniform('max_features', 0.1, 1.0),
                'max_samples': trial.suggest_uniform('max_samples', 0.5, 1.0),
                'bootstrap': trial.suggest_categorical('bootstrap', [True, False]),
                'bootstrap_features': trial.suggest_categorical('bootstrap_features', [True, False])
            }

            # Train model on dataset A
            rp_source_model = BaggingRegressor(**params)
            rp_source_model.fit(A_X_train, A_Y_train)
            yhat2 = rp_source_model.predict(A_tar_x_scaled)
            mse3 = mean_squared_error(A_tar_y_scaled, yhat2)
            mape3 = mean_absolute_percentage_error(A_tar_y_scaled, yhat2)

            # Train model on dataset B
            rc_source_model = BaggingRegressor(**params)
            rc_source_model.fit(B_X_train, B_Y_train)
            yhat4 = rc_source_model.predict(B_tar_x_scaled)
            mse5 = mean_squared_error(B_tar_y_scaled, yhat4)
            mape5 = mean_absolute_percentage_error(B_tar_y_scaled, yhat4)

            return mse3 + mse5  # Minimize the combined error

        # Create the study and optimize
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=100)

        # Get the best parameters
        best_params = study.best_params

        # Train final models with the best parameters
        rp_source_model = BaggingRegressor(**best_params)
        rp_source_model.fit(A_X_train, A_Y_train)
        yhat2 = rp_source_model.predict(A_tar_x_scaled)
        mse3 = mean_squared_error(A_tar_y_scaled, yhat2)
        mape3 = mean_absolute_percentage_error(A_tar_y_scaled, yhat2)

        rc_source_model = BaggingRegressor(**best_params)
        rc_source_model.fit(B_X_train, B_Y_train)
        yhat4 = rc_source_model.predict(B_tar_x_scaled)
        mse5 = mean_squared_error(B_tar_y_scaled, yhat4)
        mape5 = mean_absolute_percentage_error(B_tar_y_scaled, yhat4)
        print(f"Best paramaters that I obtained from the bagging part{best_params}")
        return mse3, mape3, mse5, mape5, 
