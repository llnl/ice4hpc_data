import yaml
import optuna
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf
import random
from sklearn.ensemble import AdaBoostRegressor
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Activation, Dropout, Flatten, Input, Dense, concatenate
from sklearn.metrics import accuracy_score, precision_score, recall_score, r2_score, mean_squared_error, mean_absolute_percentage_error
from tensorflow.keras.models import Model, Sequential, load_model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import preprocessing
import dataloader
from preprocessing import preprocessor
from dataloader import dataLoader
import sys
import os
import os.path
import csv
from sklearn.neighbors import KNeighborsRegressor
#import ensemRegressor
#import optunatransformator1
import util
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.impute import SimpleImputer

class AdaBoost():
  def __init__(self, num_of_estimators):
    self.num_of_estimators = int(num_of_estimators)
  def __call__(self, config_yaml, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, B_X_train, B_Y_train, B_tar_x_scaled, B_tar_y_scaled):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    #callback2 = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=40)
    folder_name = "RF"
    #tar_x_train, tar_x_test, tar_y_train, tar_y_test = processor.get_train_test_target(test_size = 0.9, rand_state=i*50)
    """
    """

    # Handle missing values
    # Impute missing values for dataset A
    imputer_A = SimpleImputer(missing_values=np.nan,strategy='mean')
    A_X_train = imputer_A.fit_transform(A_X_train)
    A_tar_x_scaled = imputer_A.transform(A_tar_x_scaled)

    B_X_train_df = pd.DataFrame(B_X_train)
    B_tar_x_scaled_df = pd.DataFrame(B_tar_x_scaled)
    B_X_train_df, B_tar_x_scaled_df = B_X_train_df.align(B_tar_x_scaled_df, join='outer', axis=1)
    B_X_train_df = B_X_train_df.fillna(np.nan)
    B_tar_x_scaled_df = B_tar_x_scaled_df.fillna(np.nan)

    B_X_train = B_X_train_df.values
    B_tar_x_scaled = B_tar_x_scaled_df.values
    B_combined = np.vstack((B_X_train, B_tar_x_scaled))
    imputer_B = SimpleImputer(missing_values=np.nan,strategy='mean')
    B_combined_imputed = imputer_B.fit_transform(B_combined)
    B_X_train = B_combined_imputed[:B_X_train.shape[0], :]
    B_tar_x_scaled = B_combined_imputed[B_X_train.shape[0]:, :]


    print("Adaboost A_X_train shape:", A_X_train.shape)
    print("Adaboost B_X_train shape:", B_X_train.shape)
    """
    parameters = { 'n_estimators': [10,30, 50],
               'loss': ["linear","square"],
               'learning_rate': [0.01, 0.05, 0.1]
             }
    grid = GridSearchCV(AdaBoostRegressor(),parameters)
    model = grid.fit(A_X_train, A_Y_train)
    print(model.best_params_,'\n')
    print(model.best_estimator_,'\n')

    params = model.best_params_
    """
    rp_source_model = AdaBoostRegressor(learning_rate=0.01, loss='linear', n_estimators=10)#(**model.best_params_)
    rp_source_model.fit(A_X_train, A_Y_train)
    yhat2 = rp_source_model.predict(A_tar_x_scaled)
    mse3 = mean_squared_error(A_tar_y_scaled, yhat2)
    mape3 = mean_absolute_percentage_error(A_tar_y_scaled, yhat2)
    print(f'mse:{mse3}')
    print(mape3)
    """
    parameters = { 'n_estimators': [10, 30, 50],
               'loss': ["linear","square"],
               'learning_rate': [0.01, 0.05, 0.1]
             }
    
    grid = GridSearchCV(AdaBoostRegressor(),parameters)
    model = grid.fit(B_X_train, B_Y_train)
    print(model.best_params_,'\n')
    print(model.best_estimator_,'\n')
    
    rc_source_model = AdaBoostRegressor(learning_rate=0.01, loss='linear', n_estimators=10) #(**params)
    rc_source_model.fit(B_X_train, B_Y_train)
    """
    yhat4 = rp_source_model.predict(B_tar_x_scaled)
    mse5 = mean_squared_error(B_tar_y_scaled, yhat4)
    mape5 = mean_absolute_percentage_error(B_tar_y_scaled, yhat4)
    print(f"mape values are {mape3},{mape5}")
    return mse3, mape3,mse5, mape5
