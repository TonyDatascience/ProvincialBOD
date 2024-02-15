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



pd.options.display.float_format = '{:,.2f}'.format
#UN='7005867'
#PW='PoP@icmarket24'
#Demo
#---------------------------------------------------------------------------------------------------------------------#
#Standard account                                      Section  setting server and broker                                           --#
#UN=51569834
#PW='bn$&jcbW7R'
#sv='ICMarketsSC-Demo'
#os.environ['TF_ENABLE_ONEDNN_OPTS']='0'
gap_timezone = pytz.timezone('Etc/GMT-5') #Run on PC
gap_timezone = pytz.timezone('Etc/GMT+2') #Run on server

#Raw account
UN=51593605
PW='6t$kPrO3kt'
sv='ICMarketsSC-Demo'

#---------------------------------------------------------------------------------------------------------------------#
FirstInstall=False
dbMarketFile="MarketTime.db"
dbOrdersFile="Orders.db"
json_file_name='forex_controls.json'
TargetMarketName='EURUSD'
TblOrders='orders_'+str(date.today())
symbol='EURUSD'
EMA_Constant=2
pre_chunk_need=30;chunk_size=100;post_chunk_need=25;TotalChunkSize=pre_chunk_need+chunk_size+post_chunk_need;
TradeSafety=20.0


TargetMarketName='EURUSD'
tp=0.00050
lot=0.05
coeff=1
ExpiredOrder=1
ExpiredPosition=25
useMT5=False
if(useMT5): 
    import MetaTrader5 as mt5

SpreadSec=10
deviation = 3
sl=5
MaxMinutes=25
AcceptLoss=-tp*coeff*lot
ServerControl='Run'
MaxRound=10000
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

pre_chunk_need=30;chunk_size=100;post_chunk_need=25;TotalChunkSize=pre_chunk_need+chunk_size+post_chunk_need;


print("Basic parameters= pre_chunk_need={},chunk_size={},post_chunk_need={},TotalChunkSize={}".format(pre_chunk_need,chunk_size,post_chunk_need,TotalChunkSize))
OriginalChunk=Based_Pkl[-1000:]

if(True):
    Number_Of_Frames=OriginalChunk.shape[0]-(pre_chunk_need+post_chunk_need)+1
    StartFrame=0
    StopFrame=Number_Of_Frames
    eAllChunks=pd.DataFrame()
    start_time=timeit.default_timer()
    for i in range(StartFrame,StopFrame):
        SmallChunk=OriginalChunk[i:(i+pre_chunk_need+post_chunk_need)]
        #print(i,"=",SmallChunk.index)
        TimeTotal=(pd.Timedelta(SmallChunk['TimeMin'].values[54]-SmallChunk['TimeMin'].values[0]).seconds)/60
        if(TimeTotal==pre_chunk_need+post_chunk_need-1):    
            #eAllChunks=pd.concat([eAllChunks,PrepRowsGrid(SmallChunk,FutureSoftmax=True)],ignore_index=True)
            eAllChunks=pd.concat([eAllChunks,PrepRowsSelected(SmallChunk,FutureSoftmax=True)],ignore_index=True)
        update_progress((i+1)/(StopFrame))
    eAllChunks.to_pickle("Data/day_BTC_Chunk.pkl")
    end_time=timeit.default_timer()
    elapsed_time=end_time - start_time
    print("working time for data preparation=",elapsed_time," sec for ",StopFrame-StartFrame," frames")
    Combine_Chunks=pd.read_pickle("Data/day_BTC_Chunk.pkl")
else:
    Combine_Chunks=pd.read_pickle("Data/day_BTC_Chunk.pkl")
if(True):
    print("HELLO")
    Profit=10
    Result=pd.DataFrame({'Target':[],'Real0':[],'Real1':[],'Real2':[],'FireRate':[],'Accuracy_Need':[],'TW_Score':[]})
    Targets=All_Y_Features
    for ColName in Targets:
            t=Selected_Rows[ColName].value_counts()
            tp_loc=ColName.find('tp')
            tp_end=ColName.find('_sl')
            tp=int(ColName[(tp_loc+2):tp_end])
            sl=int(ColName[(tp_end+3):])
            #tp*Acc-sl+Acc*sl=0 tp*Acc+Acc*sl=sl Acc(tp+sl)=sl Acc=sl/(tp+sl)
            FRate=(t[1]+t[2])/sum(t)
            Acc=(Profit+sl)/(tp+sl)
            Result.loc[len(Result)] =[ColName,t[0],t[1],t[2],FRate,Acc,FRate*0.8+1.2*Acc]
            #tp*Acc-(1-Acc)*sl
        #Result.loc[len(Result)] = [tname,t[0],t[1],t[2],(t[1]+t[2])/sum(t),(Cost+7)/(Profit+Cost+7),(Cost+10)/(Profit+Cost+10),(t[1]+t[2])/sum(t)*(1-(Cost)/(Profit+Cost))]
    print(Result)
Chosen_Y_Feature=['softmax_tp100_sl70','softmax_tp120_sl70']
OutputIndex=range(pre_chunk_need-1,Combine_Chunks.shape[0],pre_chunk_need)
Selected_Rows=Combine_Chunks.iloc[OutputIndex]
All_Y_Features=Chosen_Y_Feature
Selected_Rows['softmax_tp120_sl70'].value_counts()
#Based_Pkl
