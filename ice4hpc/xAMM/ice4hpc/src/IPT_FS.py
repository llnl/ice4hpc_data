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
import ensemRegressor
import optunatransformator1
import util
import re
class IPT_FS():
  def __init__(self, transfer_technique):
    self.transfer_technique = transfer_technique
  def __call__(self, config_yaml, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, A_tar_x_test, A_tar_y_test, B_X_train, B_Y_train, B_tar_x_scaled, B_tar_y_scaled, B_tar_x_test, B_tar_y_test)#, fname, rank, preprocessor1, preprocessor2):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    target_app = "ice4hpc"
    
    csv_path = os.getcwd()+global_config["csv_path"]
    #indices_path = os.getcwd()+global_config["indices_path"]
    fig_path = os.getcwd()+global_config["fig_path"]
    
    #use_case_specific_config = global_config[self.transfer_technique]
    use_case_specific_config = global_config["IPT"]["IPT_params"]
    test_samples = global_config['test_samples']
    folder_name = "one_out_FS_IPT"
    """
    if self.transfer_technique=="linear_probing":
      folder_name ="LP"
      self.transfer_permission = True
    elif self.transfer_technique=="fine_tuning":
      folder_name = "FT"
      self.transfer_permission = False
    """
    source_model = util.sorceModelLoader( A_X_train, A_Y_train, False, 0, False, global_config, target_app, False,os.getcwd()+global_config["source_model1"], os.getcwd()+global_config["source_model_weights1"])
    predictions = source_model.predict(A_tar_x_test)
    mse0 = mean_squared_error(A_tar_y_test, predictions)
    #ground_truth = preprocessor1.transform(A_tar_y_test)
    #model_predictions = preprocessor1.transform(predictions)
    mape0 = mean_absolute_percentage_error(A_tar_y_test, predictions)
    transformator = optunatransformator1.Transformator(dim = A_X_train.shape[1], numOfLayersE = use_case_specific_config["layers"] , neuronsE = use_case_specific_config["neurons"] , activationE= "relu")
    optimizer = tf.keras.optimizers.Adam(learning_rate= use_case_specific_config["lr"])
    #util.dataToCsv(A_tar_y_scaled, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-fewshot-{fname}-{rank}.csv")
    for epch in range(1000):
      #print(f"x2 {x2}")
      #print(f"lb2 {lb2}")
      optunatransformator1.train( transformator, source_model, optimizer, A_tar_x_scaled, A_tar_y_scaled)
    transformed = transformator(A_tar_x_test)
    predictions2 = source_model.predict(transformed)
    #util.newscatterPlot(tar_y_test, predictions2, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-{fname}-{rank}.pdf",f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-ground_truth-{fname}-{rank}.csv",  f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-predictions-{fname}-{rank}.csv","actual vs predictions")
    pp1 = np.nan_to_num(predictions2)# tf.cast(predictions0, dtype = tf.float32)
    mse2 = mean_squared_error(A_tar_y_test, pp1)
    ground_truth = A_tar_y_test #preprocessor1.transform(A_tar_y_test)
    model_predictions = pp1 #preprocessor1.transform(pp1)
    mape2 = mean_absolute_percentage_error(A_tar_y_test, pp1)
    #util.newscatterPlot(ground_truth, model_predictions, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-{fname}-{rank}.pdf",f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-ground_truth-{fname}-{rank}.csv",  f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-predictions-{fname}-{rank}.csv","actual vs predictions")
    
    #util.newscatterPlot(ground_truth, model_predictions, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-{fname}-{rank}.pdf",f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-ground_truth-{fname}-{rank}.csv",  f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-predictions-{fname}-{rank}.csv","actual vs predictions")    



    source_model = util.sorceModelLoader( B_X_train, B_Y_train, False, 0, False, global_config, target_app, False,os.getcwd()+global_config["source_model2"], os.getcwd()+global_config["source_model_weights2"])
    predictions3 = source_model.predict(B_tar_x_test)
    mse3 = mean_squared_error(B_tar_y_test, predictions3)
    #ground_truth = preprocessor2.transform(B_tar_y_test)
    #model_predictions = preprocessor2.transform(predictions3)
    mape3 = mean_absolute_percentage_error(B_tar_y_test, predictions3)
    transformator = optunatransformator1.Transformator(dim = B_X_train.shape[1], numOfLayersE = use_case_specific_config["layers"] , neuronsE = use_case_specific_config["neurons"] , activationE= "relu")
    optimizer = tf.keras.optimizers.Adam(learning_rate= use_case_specific_config["lr"])
    #util.dataToCsv(lb2, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-c-{folder_name}-fewshot-{fname}-{rank}.csv")
    for epch in range(1000):
      #print(f"x2 {x2}")
      #print(f"lb2 {lb2}")
      optunatransformator1.train( transformator, source_model, optimizer, B_tar_x_scaled, B_tar_y_scaled)
    transformed = transformator(B_tar_x_test)
    predictions4 = source_model.predict(transformed)
    pp1 = np.nan_to_num(predictions4)# tf.cast(predictions0, dtype = tf.float32)
    mse4 = mean_squared_error(B_tar_y_test, pp1)
    ground_truth = B_tar_y_test #preprocessor2.transform(B_tar_y_test)
    model_predictions = pp1 #preprocessor2.transform(pp1)
    mape4 = mean_absolute_percentage_error(B_tar_y_test, pp1)
    #util.newscatterPlot(ground_truth, model_predictions, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-c-{folder_name}-{fname}-{rank}.pdf",f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-c-{folder_name}-ground_truth-{fname}-{rank}.csv",  f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-c-{folder_name}-predictions-{fname}-{rank}.csv","actual vs predictions")
    return mse2, mape2, mse4, mape4 

