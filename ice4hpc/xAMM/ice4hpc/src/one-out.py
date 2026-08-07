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
from sklearn.metrics import accuracy_score, precision_score, recall_score, r2_score, mean_squared_error
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
import ensemRegressor
import optunatransformator1
import util

class random_forrest():
  def __init__(self, num_of_estimators):
    self.num_of_estimators = int(num_of_estimators)
  def __call__(self, config_yaml, result_path, test_samples, target_app, num_of_frozen_layers, processor, source_features, source_labels, rank):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    #callback2 = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=40)
    folder_name = "RF"
    for i in range(rank, rank+1):
      os.makedirs(os.path.dirname(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-{folder_name}-results-{rank}.csv"), exist_ok=True)
      fileI = open(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-{folder_name}-results-{rank}.csv", "w")
      writer = csv.writer(fileI)
      tar_x_train, tar_x_test, tar_y_train, tar_y_test = processor.get_train_test_target(test_size = 0.9, rand_state=i*50)
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
        clf1 = RandomForestRegressor(n_estimators=self.num_of_estimators)
        #clf1.fit(source_features, source_labels.ravel())
        """
        train_pred = clf1.predict(X_train)
        clf2 = RandomForestRegressor(n_estimators=100)
        t2_prime = tf.cast(train_pred , dtype = tf.float64)
        t2_prime = tf.reshape(t2_prime, (t2_prime.shape[0],1))
        new_test_Input = tf.concat([X_train, t2_prime], 1)
        clf2.fit(new_test_Input, y_train.ravel())
        """
        clf1.fit(x2,lb2)
        predictions0 = clf1.predict(tar_x_test)
        mse0 = mean_squared_error(tar_y_test, predictions0)
        rowArr.append(mse0)
        writer.writerow(rowArr)
      fileI.close()

