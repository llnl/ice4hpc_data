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
class generator():
  def __init__(self, transfer_technique):
    self.transfer_technique = transfer_technique
  def __call__(self, config_yaml, target_app, preprocessor1, A_X_train, A_Y_train, A_tar_x_scaled, A_tar_y_scaled, rank):
    with open(config_yaml, "r") as f:
      global_config= yaml.load(f, Loader=yaml.FullLoader)
    csv_path = os.getcwd()+global_config["csv_path"]
    indices_path = os.getcwd()+global_config["indices_path"]
    fig_path = os.getcwd()+global_config["fig_path"]
    #use_case_specific_config = global_config[self.transfer_technique]
    use_case_specific_config = global_config["IPT2"]["IPT_params"]
    test_samples = global_config['test_samples']
    folder_name = "IPT"



    """
    if self.transfer_technique=="linear_probing":
      folder_name ="LP"
      self.transfer_permission = True
    elif self.transfer_technique=="fine_tuning":
      folder_name = "FT"
      self.transfer_permission = False
    """
    for nu_of_frozen_layers in use_case_specific_config["num_of_frozen_layers"]:
      for i in range(rank, rank+1):
        print(f"************Rank {rank} is entering freezing layer {nu_of_frozen_layers}*******")
        """
        if re.search("LP",folder_name):
          folder_name = f"LP{nu_of_frozen_layers}"
        """
        os.makedirs(os.path.dirname(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-results-{rank}-MSE.csv"), exist_ok=True)
        os.makedirs(os.path.dirname(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-results-{rank}-MAPE.csv"), exist_ok=True)
        fileI = open(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-results-{rank}-MSE.csv", "w")
        fileJ = open(f"{csv_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-results-{rank}-MAPE.csv", "w")
        writerI = csv.writer(fileI)
        writerJ = csv.writer(fileJ)
        tar_x_train, tar_x_test, tar_y_train, tar_y_test = preprocessor1.get_train_test_target(test_size = 0.9, rand_state=i*50)
        ech = 5
        for j in test_samples:
          #n = j/10.0
          rowMSE = []
          rowMAPE = []
          if isinstance(j, int):
            fname = f"{j}-samples"
            fidx = j/5
          else:
            fname = f"{j}-percent"
            fidx = int(j*10.0)
          tar_x_scaled, tar_y_scaled = preprocessor1.get_tar_train()
          print("before the sample loader")
          x2, lb2, tar_x_scaled, tar_y_scaled = util.sampleLoader(tar_x_scaled, tar_y_scaled,f"{indices_path}/{target_app}-q-r-indices-{rank}-{fname}.csv" ,j)
          print(f"The indices path is {indices_path}/{target_app}-indices-{rank}-{fname}.csv")
          print("After the sample loader")

          source_model = util.sorceModelLoader( A_X_train, A_Y_train, False, nu_of_frozen_layers, False, global_config, target_app, False,os.getcwd()+global_config["source_model1"], os.getcwd()+global_config["source_model_weights1"])
          predictions = source_model.predict(tar_x_test)
          mse0 = mean_squared_error(tar_y_test, predictions)
          ground_truth = preprocessor1.transform(tar_y_test)
          model_predictions = preprocessor1.transform(predictions)
          mape0 = mean_absolute_percentage_error(ground_truth, model_predictions)
          transformator = optunatransformator1.Transformator(dim = A_X_train.shape[1], numOfLayersE = use_case_specific_config["layers"] , neuronsE = use_case_specific_config["neurons"] , activationE= "relu")
          optimizer = tf.keras.optimizers.Adam(learning_rate= use_case_specific_config["lr"])
          util.dataToCsv(lb2, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-fewshot-{fname}-{rank}.csv")
          for epch in range(1000):
            print(f"x2 {x2}")
            print(f"lb2 {lb2}")
            optunatransformator1.train( transformator, source_model, optimizer, x2, lb2)
          transformed = transformator(tar_x_test)
          predictions2 = source_model.predict(transformed)
          #util.newscatterPlot(tar_y_test, predictions2, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-{fname}-{rank}.pdf",f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-ground_truth-{fname}-{rank}.csv",  f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-predictions-{fname}-{rank}.csv","actual vs predictions")
          pp1 = np.nan_to_num(predictions2)# tf.cast(predictions0, dtype = tf.float32)
          mse2 = mean_squared_error(tar_y_test, pp1)

          ground_truth = preprocessor1.transform(tar_y_test)
          model_predictions = preprocessor1.transform(pp1)
          mape2 = mean_absolute_percentage_error(ground_truth, model_predictions)
          util.newscatterPlot(ground_truth, model_predictions, f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-{fname}-{rank}.pdf",f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-ground_truth-{fname}-{rank}.csv",  f"{fig_path}{folder_name}/Source-model-on-target-{target_app}-q-r-{folder_name}-predictions-{fname}-{rank}.csv","actual vs predictions")
          #mse0, mse2, mape0, mape2 = util.update_source_model(source_model, tar_x_test, tar_y_test, x2, lb2, global_config, ech)
          rowMSE.append(mse0)
          rowMSE.append(mse2)
          rowMAPE.append(mape0)
          rowMAPE.append(mape2)
          writerI.writerow(rowMSE)
          writerJ.writerow(rowMAPE)
          ech = ech * ech
        #print(f"*********Rank {rank} is finishing *************")
        fileI.close()
        fileJ.close()
    

