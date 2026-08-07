import util
import argparse
import yaml
import importlib
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
#import transfer_learning
#import optunatransformator1
#import stacked_model
#import k_regressor
import random_forrest
#import IPT
#import train_only
#import source_only
import mpi4py
#from transfer_learning import transfer_learning
#from stacked_model import stacked_model
#from k_regressor import k_regressor
from random_forrest import random_forrest
#from IPT import IPT
#from train_only import train_only
#from source_only import source_only
from mpi4py import MPI
#np.random.seed(1)  
#tf.random.set_seed(2)
#import optunannPOD
import re    
if __name__ == "__main__":
  comm = MPI.COMM_WORLD
  rank = comm.Get_rank()
  print(f"Rank is {rank}")
  #path_to_module = '/content/drive/MyDrive/'
  np.random.seed(1)  
  tf.random.set_seed(2)
  
  os.chdir("../../")
  parser = argparse.ArgumentParser()
  parser.add_argument('target_app', type=str,  help="name of the target domain")
  parser.add_argument('use_case', type=str,  help="which do want to fo from train_only, source_only, transfer_learning, random_forrest, k_regressor, IPT and stacked_model")
  parser.add_argument('yaml', type=str,  help="what will be the yaml file")
  args = parser.parse_args()
  with open(os.getcwd()+args.yaml, "r") as f:
    global_config= yaml.load(f, Loader=yaml.FullLoader)
  test_samples = global_config['test_samples']
  use_case_specific_config = global_config[args.use_case]
  #loader = dataLoader(os.getcwd()+global_config["src_path"], os.getcwd()+global_config["tar_path"])
  #loader.loadData()
  #src_x, src_y, tar_x, tar_y = loader.getXY("", "",global_config["target_label"])
  #src_x, src_y, tar_x, tar_y = loader.src_tx, loader.src_y, loader.tar_tx, loader.tar_y
  qrrploader = dataLoader(os.getcwd()+global_config["src_path1"] ,os.getcwd()+global_config["tar_path1"] )
  qrrploader.loadData()
  qrrp_src_x, qrrp_src_y, qrrp_tar_x, qrrp_tar_y = qrrploader.getXY("", "",["30"])
  qrrp_p = preprocessor(qrrp_src_x, qrrp_src_y, qrrp_tar_x, qrrp_tar_y, 0)
  qrrp_p.setTargetColumn(["30"])
  qrrp_src_tx, qrrp_src_ty = qrrploader.getSrcXY()
  qrrp_p.setSrcDFXY(qrrp_src_tx, qrrp_src_ty)
  qrrp_tar_tx, qrrp_tar_ty = qrrploader.getTarXY()
  qrrp_p.setTarDFXY(qrrp_tar_tx, qrrp_tar_ty)
  qrrp_p.preprocess()
  qrrp_tar_x_scaled, qrrp_tar_y_scaled = qrrp_p.getTargetScaled()
  qrrp_X_train, qrrp_y_train, qrrp_src_train, qrrp_src_y_train, qrrp_src_val, qrrp_src_y_val, qrrp_X_test, qrrp_y_test = qrrp_p.train_test_val( 0.05, 0.25, 42, 84) #100, 812
  qrrp_tar_x_train, qrrp_tar_x_test, qrrp_tar_y_train, qrrp_tar_y_test = qrrp_p.get_train_test_target(test_size = 0.7, rand_state=rank*50)


  rcrploader = dataLoader(os.getcwd()+global_config["src_path2"],os.getcwd()+global_config["tar_path2"] )#("LDRD/Case-1-new_labels_2/q-c/Train/","LDRD/Case-1-new_labels_2/q-c/Test/")
  rcrploader.loadData()
  rcrp_src_x, rcrp_src_y, rcrp_tar_x, rcrp_tar_y = rcrploader.getXY("", "",["30"])
  rcrp_tar_x = np.reshape(rcrp_tar_x, (rcrp_tar_x.shape[0], rcrp_tar_x.shape[1]))
  rcrp_p = preprocessor(rcrp_src_x, rcrp_src_y, rcrp_tar_x, rcrp_tar_y, 0)
  rcrp_p.setTargetColumn(["30"])
  rcrp_src_tx, rcrp_src_ty = rcrploader.getSrcXY()
  rcrp_p.setSrcDFXY(rcrp_src_tx, rcrp_src_ty)
  rcrp_tar_tx, rcrp_tar_ty = rcrploader.getTarXY()
  rcrp_p.setTarDFXY(rcrp_tar_tx, rcrp_tar_ty)
  rcrp_p.preprocess()
  rcrp_tar_x_scaled, rcrp_tar_y_scaled = rcrp_p.getTargetScaled()
  rcrp_X_train, rcrp_y_train, rcrp_src_train, rcrp_src_y_train, rcrp_src_val, rcrp_src_y_val, rcrp_X_test, rcrp_y_test = rcrp_p.train_test_val(0.05, 0.25, 42, 84)
  rcrp_tar_x_train, rcrp_tar_x_test, rcrp_tar_y_train, rcrp_tar_y_test = rcrp_p.get_train_test_target(test_size = 0.7, rand_state=rank*50)


  """
  print("Src x shape before preprocessing")
  print(src_x.shape)
  print("Tar_x shape before preprocessing")
  print(tar_x.shape)
  print("Src y before preprocessing")
  print(src_y)
  #print(f"{tar_x.shape}, {tar_y.shape}")
  p = preprocessor(src_x, src_y, tar_x, tar_y, 0)
  print("Src y after preprocessing")
  print(src_y)
  p.setTrainStorage(global_config["stdy"], global_config["storageN"])
  p.setNumOfTrials(global_config["tuning_trials"])
  p.setTrialEpochs(global_config["tuning_epochs"])
  p.setTargetColumn(global_config["target_label"])
  src_tx, src_ty = loader.getSrcXY()
  p.setSrcDFXY(src_tx, src_ty)
  tar_tx, tar_ty = loader.getTarXY()
  p.setTarDFXY(tar_tx, tar_ty)
  p.preprocess()
  tar_x_scaled, tar_y_scaled = p.getTargetScaled()
  X_train, y_train, src_train, src_y_train, src_val, src_y_val, X_test, y_test = p.train_test_val( global_config["test_split"], global_config["val_split"], global_config["rand_state"], global_config["rand_state2"])
  """
  try:
    with tf.device('/gpu:0'):
      module_name, func_name = use_case_specific_config["module_name"], use_case_specific_config["class_name"]
      module = importlib.import_module(module_name)
      func = getattr(module, func_name)
      obj = func(use_case_specific_config["init_arg"])
      obj(os.getcwd()+args.yaml, args.target_app, qrrp_p, rcrp_p, qrrp_X_train, qrrp_y_train, qrrp_tar_x_test, qrrp_tar_y_test, rcrp_X_train, rcrp_y_train,rcrp_tar_x_test, rcrp_tar_y_test, rank)
  except RuntimeError as e:
    print(e)