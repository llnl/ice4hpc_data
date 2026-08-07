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
from tensorflow.keras.models import Model, Sequential, load_model, model_from_json
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
import util
class index_maker():
  def __init__(self, transfer_technique):
    self.transfer_technique = transfer_technique
  def __call__(self, config_yaml, target_app, preprocessor1, preprocessor2, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, B_X_train, B_Y_train, B_tar_x_scaled, B_tar_y_scaled, rank):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    test_samples = global_config['test_samples'] 
    for i in range(rank, rank+1):
      tar_x_train, tar_x_test, tar_y_train, tar_y_test = preprocessor1.get_train_test_target(test_size = 0.7, rand_state=rank*50)
      for j in test_samples:
        if isinstance(j, int):
          fname = f"{j}-samples"
          fidx = j/5
        else:
          fname = f"{j}-percent"
          fidx = int(j*10.0)
        print(f" inside rank {rank} for {fname} samples")
        tar_x_scaled, tar_y_scaled = preprocessor1.get_tar_train() #getTargetScaled()
        print("******tar_x_scaled*****")
        print(tar_x_scaled)
        x2, lb2, tar_x_scaled, tar_y_scaled = util.sampleMaker(tar_x_scaled, tar_y_scaled, f"{indices_path}/{target_app}-q-r-indices-{rank}-{fname}.csv" , j)
        print(f"length of x2 {len(x2)}")
        print(f"length of lb2 {len(lb2)}")
        print(f"length of tar_x_scaled {len(tar_x_scaled)}")
        print(f"length of tar_y_scaled {len(tar_y_scaled)}")


      tar_x_train, tar_x_test, tar_y_train, tar_y_test = preprocessor2.get_train_test_target(test_size = 0.7, rand_state=rank*50)
      for j in test_samples:
        if isinstance(j, int):
          fname = f"{j}-samples"
          fidx = j/5
        else:
          fname = f"{j}-percent"
          fidx = int(j*10.0)
        print(f" inside rank {rank} for {fname} samples")
        tar_x_scaled, tar_y_scaled = preprocessor2.get_tar_train() #getTargetScaled()
        print("******tar_x_scaled*****")
        print(tar_x_scaled)
        x2, lb2, tar_x_scaled, tar_y_scaled = util.sampleMaker(tar_x_scaled, tar_y_scaled, f"{indices_path}/{target_app}-q-c-indices-{rank}-{fname}.csv" , j)
        print(f"length of x2 {len(x2)}")
        print(f"length of lb2 {len(lb2)}")
        print(f"length of tar_x_scaled {len(tar_x_scaled)}")
        print(f"length of tar_y_scaled {len(tar_y_scaled)}")

