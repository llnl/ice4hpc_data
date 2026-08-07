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
from sklearn.preprocessing import OneHotEncoder
class dataLoader():
  def __init__(self, src_path, tar_path):
    self.src_path = src_path
    self.tar_path = tar_path
    self.snames = []
    self.tnames = []
  def lData(self):
    i = 0
    for filename in os.listdir(self.src_path):
      df = pd.read_csv(self.src_path+filename)
      mn = df.mean(skipna=True)
      df = df.fillna(mn)
      #df = df.dropna()
      df.reset_index(drop=True, inplace=True)
      ff = filename.split(".")
      #df["Domain"] = ff[0]
      for k in range(len(df)):
        self.snames.append(ff[0])
      if i==0:
        self.src_d = df
      else:
        self.src_d = pd.concat([self.src_d, df], axis=0)
      i = i+1
    self.src_d.reset_index(drop=True, inplace=True)
    j = 0
    for filename in os.listdir(self.tar_path):
      df = pd.read_csv(self.tar_path+filename)
      mn = df.mean(skipna=True)
      df = df.fillna(mn)
      #df = df.dropna()
      df.reset_index(drop=True, inplace=True)
      ff = filename.split(".")
      #df["Domain"] = ff[0]
      for k in range(len(df)):
        self.tnames.append(ff[0])
      #self.tnames.append(ff[0])
      #print(df)
      if j==0:
        self.tar_d = df
      else:
        self.tar_d = pd.concat([self.tar_d, df], axis=0)
      j = j + 1
    self.tar_d.reset_index(drop=True, inplace=True)
  def gData(self):
    return self.src_d, self.tar_d
  def setData(self, ts, td):
    self.src_data = ts
    self.tar_data = td
    #self.src_data["Domain"] = self.snames
    #self.tar_data["Domain"] = self.tnames
    self.src_data = self.src_data.dropna()
    self.tar_data = self.tar_data.dropna()

  def loadData(self):
    i = 0
    for filename in os.listdir(self.src_path):
      df = pd.read_csv(self.src_path+filename)
      print(f'data path here {self.src_path}{filename}')
      mn = df.mean(skipna=True)
      df = df.fillna(mn)
      #df = df.dropna()
      df.reset_index(drop=True, inplace=True)
      ff = filename.split(".")
      #df["Domain"] = ff[0]
      if i==0:
        self.src_data = df
      else:
        self.src_data = pd.concat([self.src_data, df], axis=0)
      i = i+1
    self.src_data.reset_index(drop=True, inplace=True)
    j = 0
    for filename in os.listdir(self.tar_path):
      df = pd.read_csv(self.tar_path+filename)
      print(f'src data shape here at first {self.src_data.shape} from file {self.tar_path+filename}')
      print(f'data path here:{self.tar_path}/{filename}')
      mn = df.mean(skipna=True)
      df = df.fillna(mn)
      #df = df.dropna()
      df.reset_index(drop=True, inplace=True)
      ff = filename.split(".")
      #df["Domain"] = ff[0]
      #print(df)
      if j==0:
        self.tar_data = df
      else:
        self.tar_data = pd.concat([self.tar_data, df], axis=0) 
      j = j + 1
    self.tar_data.reset_index(drop=True, inplace=True)
  def getData(self):
    return self.src_data, self.tar_data

  def getXY(self, colName, rowName, targetColumn):
    #if datasetName == "perfvar":
    #  application = rowName
    #  self.src_data = self.src_data.loc[self.src_data['application']!= application]
    #  self.tar_data = self.tar_data.loc[self.tar_data['application']== application]
    """
    s_arr = self.src_data["Domain"].unique()
    t_arr = self.tar_data["Domain"].unique()
    for name in t_arr:
      dat = []
      for i in range(len(self.src_data.columns)):
        dat.append(0)
      dat[-1]=name
      self.src_data.loc[len(self.src_data.index)] = dat
    for name in s_arr:
      dat = []
      for i in range(len(self.tar_data.columns)):
        dat.append(0)
      dat[-1]=name
      self.tar_data.loc[len(self.tar_data.index)] = dat

    ##one hot encoding
    self.src_data = pd.get_dummies(self.src_data, columns=["Domain"], drop_first=False)
    self.tar_data = pd.get_dummies(self.tar_data, columns=["Domain"], drop_first=False)
    ##remove extra inserted rows
    for name in t_arr:
        self.src_data = self.src_data.drop([len(self.src_data.index)-1])
    for name in s_arr:
        self.tar_data = self.tar_data.drop([len(self.tar_data.index)-1])
    """
    ##listing other string valued columns in source
    stringColumns = []
    for i in range(len(self.src_data.columns)):
      if self.src_data[self.src_data.columns[i]].dtypes == "object":
        stringColumns.append(self.src_data.columns[i])
    for i in range(len(self.tar_data.columns)):
      if self.tar_data[self.tar_data.columns[i]].dtypes == "object":
        stringColumns.append(self.tar_data.columns[i])
    stringColumns = list(set(stringColumns))
    ##apply one hot encoding to other string columns on source
    print(f"src string columns {stringColumns}")
    print(self.src_data)
    print("===========")
    cls = []
    for sc in stringColumns:
      cls = cls + list(self.src_data[sc].unique())
    #cls = list(set(cls))
    print(f"cls {cls}")
    cls = [ i for i in range(len(cls))]
    oe_style = OneHotEncoder()
    oe_results = oe_style.fit_transform(self.src_data[stringColumns])
    oe = pd.DataFrame(oe_results.toarray(), columns=cls)
    print(f'oe shape here {oe}')
    self.src_data = self.src_data.drop(stringColumns, axis=1)
    print('The shape of data is {self.src_data}')
    self.src_data = pd.concat([self.src_data, oe], axis=1)
    #self.src_data = pd.get_dummies(self.src_data, columns = stringColumns, drop_first=False)
    print(f'src data shape here {self.src_data.shape}')

    #Columns to be omitted
    omitColumns = []
    omitColumns.append(targetColumn)
    #self.src_ty = self.src_data[[targetColumn]]
    self.src_ty = self.src_data[targetColumn]
    self.src_y = self.src_data.loc[:, targetColumn].values
    #inds = [i for i,f in enumerate(self.src_data.columns) if f not in omitColumns]
    #print(inds)
    #self.src_data = self.src_data.drop([targetColumn], axis=1)
    self.src_data = self.src_data.drop(targetColumn, axis=1)
    self.src_tx = self.src_data
    self.src_x = self.src_data.values

    ##listing other string valued columns in target
    #stringColumns = []
    #for i in range(len(self.tar_data.columns)):
    #  if self.tar_data[self.tar_data.columns[i]].dtypes == "object":
    #    stringColumns.append(self.tar_data.columns[i])
    ##apply one hot encoding to other string columns on source
    print(f"tar string columns {self.tar_data[stringColumns]}")
    print(f"tar data {self.tar_data}")
    oe_results = oe_style.transform(self.tar_data[stringColumns])
    oe = pd.DataFrame(oe_results.toarray(), columns=cls)
    self.tar_data = self.tar_data.drop(stringColumns, axis=1)
    self.tar_data = pd.concat([self.tar_data, oe], axis=1)

    #self.tar_data = pd.get_dummies(self.tar_data, columns = stringColumns, drop_first=False)
    #Columns to be omitted
    omitColumns = [ ]
    omitColumns.append(targetColumn)
    #self.tar_ty = self.tar_data[[targetColumn]]
    self.tar_ty = self.tar_data[targetColumn]
    self.tar_y = self.tar_data.loc[:, targetColumn].values
    #inds = [i for i,f in enumerate(self.tar_data.columns) if f not in omitColumns]
    #print(inds)
    #self.tar_data = self.tar_data.drop([targetColumn], axis =1)
    self.tar_data = self.tar_data.drop(targetColumn, axis =1)
    self.tar_tx = self.tar_data
    self.tar_x = self.tar_data.values

    #print(omitColumns)
    print("Src Columns########################")
    print("loading src_x")
    print(self.src_x)
    print("loading src_y")
    print(self.src_y)
    for name in list(self.src_data.columns):
        print(name)
    print("Tar Columns ****************************")
    print("loading tar_x")
    print(self.tar_x)
    print("loading tar_y")
    print(self.tar_y)
    for name in list(self.tar_data.columns):
        print(name)
    #print("src_x shape {self.src_x.shape
    print(self.src_x.shape)
    print(self.tar_x.shape)
    return self.src_x, self.src_y, self.tar_x, self.tar_y
  def getSrcXY(self):
    return self.src_tx, self.src_ty
  def getTarXY(self):
    return self.tar_tx, self.tar_ty
