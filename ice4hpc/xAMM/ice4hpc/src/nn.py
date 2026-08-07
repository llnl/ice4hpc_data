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
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import PCA

class nn():
  def __init__(self, num_of_estimators):
    self.num_of_estimators = int(num_of_estimators)
  def __call__(self, config_yaml, X_train, Y_train, tar_x_scaled, tar_y_scaled):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    
    # encoder = OneHotEncoder(sparse_output=False)
    # # Concatenate training and test labels for dataset A to ensure all categories are captured
    # combined_labels_A = np.concatenate([Y_train, tar_y_scaled]).reshape(-1, 1)
    # encoder_A = OneHotEncoder(sparse_output=False)
    # encoder_A.fit(combined_labels_A)
    
    # # Encode labels for dataset A
    # Y_train_encoded = encoder_A.transform(np.array(Y_train).reshape(-1, 1))
    # tar_y_scaled_encoded = encoder_A.transform(np.array(tar_y_scaled).reshape(-1, 1))
    
    # # Number of classes for dataset A and B
    # num_classes_A = Y_train_encoded.shape[1]
    
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    target_app="ice4hpc"
    #callback2 = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=40)
    folder_name = "RF"
    #tar_x_train, tar_x_test, tar_y_train, tar_y_test = processor.get_train_test_target(test_size = 0.9, rand_state=i*50)
    # X_train = np.expand_dims(X_train, axis=1)
    print(f"X_train shape here {X_train.shape}")
    rp_tree_model = util.sorceModelLoader(X_train, Y_train, False, 0, True, global_config, target_app, True, os.getcwd()+global_config["source_model1"], os.getcwd()+global_config["source_model_weights1"],output_n=1 )
    prediction = rp_tree_model.predict(tar_x_scaled) 
    mse=mean_squared_error(tar_y_scaled,prediction)
    util.scatterPlot(tar_y_scaled,prediction,os.getcwd()+global_config["fig_path"]+"actual_vs_predicted_nn.pdf","Actual_VS_Predicted")
    print(f"MSE: {mse:.8f}")
    return mse