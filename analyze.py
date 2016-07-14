#-*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import sqlite3

import numpy as np

from logger import get_logger
from stockcode import get_code_list
from settings import START_DATE
from cp_constant import *
import win32com.client

def checkData( cursor, table_name ):
    row = cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)).fetchone()
    if row is None: return False
        
    row = cursor.execute("SELECT COUNT(*) FROM '{}'".format(table_name)).fetchone()
    if row is None : return False

    return True

def makeDataFrame( code ):
    with sqlite3.connect("price.db") as con:
        cursor = con.cursor()
        table_name = code
        
        if checkData( cursor, table_name ) == False: return False
        
        df = pd.read_sql("SELECT * FROM '{}'".format(table_name), con, index_col=None)
        return df

def isMAGoldCross( code, MA1 = 20, MA2 = 60 ):
    df = makeDataFrame( code )
            
    df['short_ma'] = pd.rolling_mean(df['CLOSE'],MA1)
    df['long_ma'] = pd.rolling_mean(df['CLOSE'],MA2)
    df['signal'] = 0.0
        
    if len(df) < MA2 * 4 : return False
        
    df['signal'][MA1:] = np.where(df['short_ma'][MA1:] > df['long_ma'][MA1:], 1.0, 0.0)
    df['positions'] = 0.0
    df['positions'] = df['signal'].diff()
        
    if df['signal'][len(df)-1] == 1 and df['positions'][len(df)-1] == 1:
        return True
    else:
        return False

def isBBandSignal( code, period = 20):
    df = makeDataFrame( code )
    df['Bol_upper'] = pd.rolling_mean(df['CLOSE'], window=period) + 2* pd.rolling_std(df['CLOSE'], period, min_periods=period)
    df['Bol_lower'] = pd.rolling_mean(df['CLOSE'], window=period) - 2* pd.rolling_std(df['CLOSE'], period, min_periods=period)
    df['signal'] = 0.0
    df['signal'] = np.where(df['Bol_lower'] > df['CLOSE'], 1.0, 0.0)
    df['positions'] = 0.0
    df['positions'] = df['signal'].diff()

    if len(df) < 2: return False

    if df['signal'][len(df)-2] == 1 and df['positions'][len(df)-2] == 1:
        if df['signal'][len(df)-1] == 0 and df['positions'][len(df)-1] == -1.0:
            return True
        else:
            return False
    else:
        return False

def isMACDSignal( code, n1 = 12, n2= 26, c= 9):
    df = makeDataFrame( code )
   
    df['MACD'] = pd.ewma(df['CLOSE'], span=n1) - pd.ewma(df['CLOSE'], span=n2)
    df['MACD_Signal'] = pd.ewma(df['MACD'], span=c)
    df['signal'] = 0.0
    df['signal'] = np.where(df['MACD'] < df['MACD_Signal'], 1.0, 0.0)
    df['positions'] = 0.0
    df['positions'] = df['signal'].diff()

    if df['signal'][len(df)-1] == 1 and df['positions'][len(df)-1] == 1:
        return True
    else:
        return False

def run():
    for code, name in get_code_list():
        #res = isMAGoldCross( code, 20, 60 )
        #if res == True:
        #    print("MA20 MA60 GC {} {}".format(code,name))
        #res = isBBandSignal( code, 20 )
        #if res == True:
        #    print("BBand {} {}".format(code, name))
        res = isMACDSignal( code, 12, 26, 9)
        if res == True:
            print("MACD {} {}".format(code, name))  

if __name__ == '__main__':
    run()