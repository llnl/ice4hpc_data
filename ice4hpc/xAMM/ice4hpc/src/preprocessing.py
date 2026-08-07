import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
import random
import os
import sys
import time
#import seaborn as sns
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from numpy import random
from scipy.fft import fft, ifft, fftfreq
import copy
import scipy
from sklearn.model_selection import train_test_split
class preprocessor():
  def __init__(self, src_X, src_Y, tar_x, tar_y, scalerChoice, File=None):
    self.src_X = src_X
    self.src_Y = src_Y
    self.tar_x = tar_x
    self.tar_y = tar_y
    self.scalerChoice = scalerChoice
  def preprocess(self):
    print("################Inside Preprocess##########")
    print("src_x")
    print(self.src_X)
    print("src_y")
    print(self.src_Y)
    print("tar_x")
    print(self.tar_x)
    print("tar_y")
    print(self.tar_y)
    print("############inside Preprocess##############")
    print(f"src_x shape {self.src_X.shape}")
    print(f"tar_x shape {self.tar_x.shape}")
    if self.scalerChoice == 0:
      self.X_scaler = MinMaxScaler()
      self.Y_scaler = MinMaxScaler()
    if self.scalerChoice == 1:
      self.X_scaler = StandardScaler()
      self.Y_scaler = StandardScaler()
    #self.Y_scaler.fit(self.src_Y.reshape(-1,1))
    self.Y_scaler.fit(self.src_Y)
    self.X_scaler.fit(self.src_X)
    self.src_Y_scaled = self.Y_scaler.transform(self.src_Y)
    self.tar_y_scaled = self.Y_scaler.transform(self.tar_y)
    #self.src_Y_scaled = self.Y_scaler.transform(self.src_Y.reshape(-1,1))
    #self.tar_y_scaled = self.Y_scaler.transform(self.tar_y.reshape(-1,1))
    #print(f"{src_y_scaled.shape}, {tar_y_scaled.shape}")
    #print(f" source columns {self.src_X.columns}")
    #print(f"target columns {self.tar_x.columns}")
    """        
    self.src_X.loc[:] = self.X_scaler.transform(self.src_X)
    self.X_scaler.fit(self.tar_x)
    self.tar_x.loc[:] = self.X_scaler.transform(self.tar_x)
    self.src_X_scaled = self.src_X #self.X_scaler.transform(self.src_X)
    self.tar_x_scaled = self.tar_x #self.X_scaler.fit_transform(self.tar_x)
    """
      
    self.src_X_scaled = self.X_scaler.transform(self.src_X)
    self.tar_x_scaled = self.X_scaler.fit_transform(self.tar_x)
    """ 
    """# **Train Test validation**"""
  def getSrcDataset(self):
    if self.scalerChoice == 0:
      self.tX_scaler = MinMaxScaler()
      self.tY_scaler = MinMaxScaler()
    if self.scalerChoice == 1:
      self.tX_scaler = StandardScaler()
      self.tY_scaler = StandardScaler()
    print(self.src_tx.loc[:,])
    tx_array = self.tX_scaler.fit_transform(self.src_tx)
    self.src_tx = pd.DataFrame(tx_array, columns = self.src_tx.columns)
    print(self.src_tx)
    ty_array = self.tY_scaler.fit_transform(self.src_ty)
    self.src_ty = pd.DataFrame(ty_array, columns = self.src_ty.columns)
    self.src_df = pd.concat([self.src_tx, self.src_ty], axis=1)
    return self.src_tx, self.src_ty, self.src_df
  def getTarDataset(self, rank, test_split):
    tar_tx_array = self.tX_scaler.transform(self.tar_tx)
    self.tar_tx = pd.DataFrame(tar_tx_array, columns = self.tar_tx.columns)
    self.tar_tx, self.tar_tx_test = train_test_split(self.tar_tx, test_size = test_split, random_state=rank*50, shuffle = True, stratify = None)
    print(self.tar_tx)
    tar_ty_array = self.tY_scaler.transform(self.tar_ty)
    self.tar_ty = pd.DataFrame(tar_ty_array, columns = self.tar_ty.columns)
    self.tar_ty, self.tar_ty_test = train_test_split(self.tar_ty, test_size = test_split, random_state=rank*50, shuffle = True, stratify = None)
    self.tar_df = pd.concat([self.tar_tx, self.tar_ty], axis=1)
    self.tar_test = pd.concat([self.tar_tx_test, self.tar_ty_test], axis=1)
    return self.tar_tx, self.tar_ty, self.tar_df, self.tar_tx_test, self.tar_ty_test, self.tar_test

  def getActualSamples(self, lst, domain, col):
    if domain == "target":
      if col == "x":
        lst = self.X_scaler.inverse_transform(lst)
        print(lst)
      elif col == "y":
        lst = self.Y_scaler.inverse_transform(lst)
        print(lst)
    return lst
  def train_test_val(self, test_size_, val_size, rand_state, rand_state2=0):
    print(self.src_X_scaled)
    print(self.src_Y_scaled)
    self.X_train, self.X_test, self.y_train, self.y_test = train_test_split( self.src_X_scaled, self.src_Y_scaled, test_size=test_size_, random_state=rand_state, shuffle = True, stratify = None)
    self.src_train, self.src_val, self.src_y_train, self.src_y_val = train_test_split( self.X_train, self.y_train, test_size=val_size, random_state= rand_state2, shuffle = True, stratify = None)
    return self.X_train, self.y_train, self.src_train, self.src_y_train, self.src_val, self.src_y_val, self.X_test, self.y_test
  def get_train_test_target(self, test_size, rand_state = 0):
    self.tar_x_train, self.tar_x_test, self.tar_y_train, self.tar_y_test = train_test_split( self.tar_x_scaled, self.tar_y_scaled, test_size=test_size, random_state=rand_state, shuffle = True, stratify = None)
    return self.tar_x_train, self.tar_x_test, self.tar_y_train, self.tar_y_test
  def get_tar_train(self):
    return self.tar_x_train, self.tar_y_train
  def get_tar_test(self):
    return self.tar_x_test, self.tar_y_test
  def getSrcTestSamples(self):
    return self.X_test, self.y_test
  def getTargetScaled(self):
    return self.tar_x_scaled, self.tar_y_scaled
  def setTrainStorage(self, study_name, storage_name):
    self.study_name = study_name
    self.storage_name = storage_name
  def getTrainStorage(self):
    return self.study_name, self.storage_name
  def setNumOfTrials(self, num):
    self.NumOfTrials = num
  def getNumOfTrials(self):
    return self.NumOfTrials
  def setTrialEpochs(self, num):
    self.TrialEpochs = num
  def getTrialEpochs(self):
    return self.TrialEpochs
  def setTargetColumn(self, name):
    self.targetColumn = name
  def getTargetColName(self):
    return self.targetColumn
  def setSrcDFXY(self, X, Y):
    self.src_tx = X
    self.src_ty = Y
  def setTarDFXY(self, X, Y):
    self.tar_tx = X
    self.tar_ty = Y
  def transform(self, data):
    return self.Y_scaler.inverse_transform(data)
