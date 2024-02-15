import numpy as np
import pandas as pd
import copy
import matplotlib.pyplot as plt 
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import Dense, Input, Dropout, LSTM, Activation, Conv1D,MaxPooling1D,Flatten,GlobalAveragePooling1D,GlobalMaxPooling1D
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.initializers import glorot_uniform
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import layers
from keras.layers import Flatten
from keras import backend as K
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.metrics import mean_squared_error
import timeit
import pickle
import joblib
from collections import Counter
from sklearn.tree import plot_tree
from sklearn.ensemble import RandomForestClassifier
from IPython.display import display
from scipy.signal import butter,filtfilt
import sqlite3
import time
from datetime import datetime,date, timedelta
from random import randint, randrange
import copy
import sys
import timeit
#from gs_json import *
import json
import sys
import colorama
import timeit
from colorama import Fore, Back, Style
import warnings
import os
import pytz
import json
import os.path
import logging
import math
from core import *

import streamlit as st
from streamlit_jupyter import StreamlitPatcher, tqdm
StreamlitPatcher().jupyter() 
model_file_120_70='Models/cnn_100_70_Feb_13.keras'
scalerfile_120_70='Models/cnn_100_70_scaler_Feb_13.sav'
model_file_100_70='Models/cnn_120_70_Feb_14.keras'
scalerfile_100_70='Models/cnn_120_70_scaler_Feb_14.sav'
std_scaler_120_70=joblib.load(scalerfile_120_70)
model_cnn3_120_70=tf.keras.models.load_model(model_file_120_70)
std_scaler_100_70=joblib.load(scalerfile_100_70)
model_cnn3_100_70=tf.keras.models.load_model(model_file_100_70)
#Step 1: Read CSV
CSV_Files=['Data/BTCUSD_M1_2024.csv']
TestSystem=True
if(TestSystem):
    CollectivePD=pd.DataFrame()
    for iFile in CSV_Files:
        tmp_csv=pd.read_csv(iFile,sep='\t')
        OldCol=tmp_csv.columns
        tmp_csv.columns = ['Date','Time', 'Open', 'High','Low','Close','Volume','RealVolume','Spread']
        NewCol=tmp_csv.columns
        print("Based column names={}, \nNew Column names={}".format(OldCol,NewCol))
        tmp_csv=tmp_csv.assign(TimeMin=pd.to_datetime(tmp_csv['Date'] + " " + tmp_csv['Time']))
        first_column = tmp_csv.pop('TimeMin') 
        tmp_csv.insert(0, 'TimeMin', first_column) 
        tmp_csv=tmp_csv.drop(['Date','Time'], axis=1)
        CollectivePD=pd.concat([CollectivePD,tmp_csv],axis=0)
    Based_Pkl=CollectivePD
else:
    if(False):
        CollectivePD=pd.DataFrame()
        for iFile in CSV_Files:
            tmp_csv=pd.read_csv(iFile,sep='\t')
            OldCol=tmp_csv.columns
            tmp_csv.columns = ['Date','Time', 'Open', 'High','Low','Close','Volume','RealVolume','Spread']
            NewCol=tmp_csv.columns
            print("Based column names={}, \nNew Column names={}".format(OldCol,NewCol))
            tmp_csv=tmp_csv.assign(TimeMin=pd.to_datetime(tmp_csv['Date'] + " " + tmp_csv['Time']))
            first_column = tmp_csv.pop('TimeMin') 
            tmp_csv.insert(0, 'TimeMin', first_column) 
            tmp_csv=tmp_csv.drop(['Date','Time'], axis=1)
            CollectivePD=pd.concat([CollectivePD,tmp_csv],axis=0)
        CollectivePD.to_pickle("Data/dbased_all_csv.pkl")
        Based_Pkl=pd.read_pickle("Data/dbased_all_csv.pkl")
    else:
        Based_Pkl=pd.read_pickle("Data/dbased_all_csv.pkl")
st.title("Hello")
st.title(testImport("Hoola"))
#Based_Pkl
