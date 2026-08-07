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


class nn2():
  def __init__(self, num_of_estimators):
    self.num_of_estimators = int(num_of_estimators)
  def __call__(self, config_yaml, target_app, preprocessor, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, rank):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    #target_app="ice4hpc"
    #callback2 = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=40)
    folder_name = "RF"
    #tar_x_train, tar_x_test, tar_y_train, tar_y_test = processor.get_train_test_target(test_size = 0.9, rand_state=i*50)

    rp_tree_model = util.sorceModelLoader(A_X_train, A_Y_train, False, 0, True, global_config, target_app, True, os.getcwd()+global_config["source_model1"], os.getcwd()+global_config["source_model_weights1"] )
    yhat2 = rp_tree_model.predict(A_tar_x_scaled)
    mse3 = mean_squared_error(A_tar_y_scaled, yhat2)
    mape3 = mean_absolute_percentage_error(A_tar_y_scaled, yhat2)
    print(mse3)
    print(mape3)
    """    
    rc_source_model = util.sorceModelLoader(B_X_train, B_Y_train, False, 0, True, global_config, target_app, True, os.getcwd()+global_config["source_model2"], os.getcwd()+global_config["source_model_weights2"] )
    yhat4 = rc_source_model.predict(B_tar_x_scaled)
    mse5 = mean_squared_error(B_tar_y_scaled, yhat4)
    mape5 = mean_absolute_percentage_error(B_tar_y_scaled, yhat4)
    print(mse5)
    print(mape5)
    """
    return mse3, mape3






