import importlib
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
#import optunatransformator1
import util

class one_out():
  def __init__(self, num_of_estimators):
    self.num_of_estimators = int(num_of_estimators)
  def __call__(self, config_yaml, target_app, preprocessor1, preprocessor2, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, B_X_train, B_Y_train, B_tar_x_scaled, B_tar_y_scaled, rank):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    #callback2 = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=40)
    folder_name = "one_out"
    list_of_classes = global_config["one_out"]["list_of_classes"]
    list_of_class_args = global_config["one_out"]["list_of_class_args"]
    for i in range(rank, rank+1):
      os.makedirs(os.path.dirname(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-{folder_name}-results-{rank}-MSE.csv"), exist_ok=True)
      os.makedirs(os.path.dirname(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-{folder_name}-results-{rank}-MAPE.csv"), exist_ok=True)
      fileI = open(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-{folder_name}-results-{rank}-MSE.csv", "w")
      fileJ = open(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-{folder_name}-results-{rank}-MAPE.csv", "w")
      writerI = csv.writer(fileI)
      writerJ = csv.writer(fileJ)
      class_number = 0
      for module_name in list_of_classes:
        module = importlib.import_module(module_name)
        func = getattr(module, module_name)
        obj = func(list_of_class_args[class_number])
        mse0, mape0, mse1, mape1 = obj(config_yaml, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, B_X_train, B_Y_train, B_tar_x_scaled, B_tar_y_scaled)
        rowMSE =[]
        rowMAPE = []
        rowMSE.append(module_name)
        rowMSE.append(mse0)
        rowMSE.append(mse1)
        writerI.writerow(rowMSE)
        rowMAPE.append(module_name)
        rowMAPE.append(mape0)
        rowMAPE.append(mape1)
        writerJ.writerow(rowMAPE)
        class_number = class_number + 1
      fileI.close()
      fileJ.close()

