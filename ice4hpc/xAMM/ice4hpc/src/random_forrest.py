import yaml
import optuna
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf
import random
from sklearn.ensemble import RandomForestRegressor
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
#import ensemRegressor
#import optunatransformator1
import util
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.impute import SimpleImputer

class random_forrest():
  def __init__(self, num_of_estimators):
    self.num_of_estimators = int(num_of_estimators)
  def __call__(self, config_yaml, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, B_X_train, B_Y_train, B_tar_x_scaled, B_tar_y_scaled):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    #callback2 = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=40)
    folder_name = "RF"
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
    #tar_x_train, tar_x_test, tar_y_train, tar_y_test = processor.get_train_test_target(test_size = 0.9, rand_state=i*50)
    """
    for j in test_samples:
      if isinstance(j, int):
        fname = f"{j}-samples"
        fidx = j/5
      else:
        fname = f"{j}-percent"
        fidx = int(j*10.0)
      n = j/10
      tar_x_scaled, tar_y_scaled = processor.get_tar_train()
      x2, lb2, tar_x_scaled, tar_y_scaled = util.sampleLoader(tar_x_scaled, tar_y_scaled,f"{indices_path}/{target_app}-indices-{rank}-{fname}.csv" ,j)
      rowArr = []
    """
    #clf1 = RandomForestRegressor(n_estimators=self.num_of_estimators)
    #clf1.fit(source_features, source_labels.ravel())
    """
    
    parameters = { 'criterion' : ['friedman_mse','squared_error'],
              'max_features' : ['log2','sqrt',None],
              'n_estimators': [10, 30, 50],
              'max_depth': [5, 10, 15],
              'min_samples_split': [2, 5]
             }
    grid = GridSearchCV(RandomForestRegressor(),parameters)
    model = grid.fit(A_X_train, A_Y_train)
    print(model.best_params_,'\n')
    print(model.best_estimator_,'\n')
    
    params =model.best_params_
    """
    rp_tree_model = RandomForestRegressor(criterion='friedman_mse', max_depth=5,
                      max_features='sqrt', min_samples_split=5,
                      n_estimators=10) #(**params)
    #rp_tree_model = MultiOutputRegressor(rp_model)
    rp_tree_model.fit(A_X_train, A_Y_train)
    yhat2 = rp_tree_model.predict(A_tar_x_scaled)
    mse3 = mean_squared_error(A_tar_y_scaled, yhat2)
    mape3 = mean_absolute_percentage_error(A_tar_y_scaled, yhat2)
    print(mse3)
    print(mape3)
    """
    grid = GridSearchCV(RandomForestRegressor(),parameters)
    model = grid.fit(B_X_train, B_Y_train)
    print(model.best_params_,'\n')
    print(model.best_estimator_,'\n')
    params = model.best_params_ #{'criterion': 'squared_error', 'max_depth': 5, 'max_features': 'auto', 'min_samples_split': 2, 'n_estimators': 10}
    
    rc_source_model = RandomForestRegressor(criterion='friedman_mse', max_depth=5,
                      max_features='sqrt', min_samples_split=5,
                      n_estimators=10) #(**params)
    #rc_source_model = MultiOutputRegressor(rc_model)
    rc_source_model.fit(B_X_train, B_Y_train)
    """
    yhat4 = rp_tree_model.predict(B_tar_x_scaled)
    mse5 = mean_squared_error(B_tar_y_scaled, yhat4)
    mape5 = mean_absolute_percentage_error(B_tar_y_scaled, yhat4)
    print(f"here is the mape values of RF{mape3},{mape5}")
    return mse3, mape3, mse5, mape5
