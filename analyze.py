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


def isMAGoldCross( code, MA1, MA2 ):
    with sqlite3.connect("price.db") as con:
        cursor = con.cursor()
        table_name = code
        
        if checkData( cursor, table_name ) == False: return False
        
        df = pd.read_sql("SELECT * FROM '{}' order by 'DATE' ASC".format(table_name), con, index_col=None)
        df
        df['short_ma'] = pd.rolling_mean(df['CLOSE'],MA1)
        df['long_ma'] = pd.rolling_mean(df['CLOSE'],MA2)
        df['signal'] = 0.0
        
        if len(df) < MA2 * 4 : return False
        
        df['signal'][MA1:] = np.where(df['short_ma'][MA1:] > df['long_ma'][MA1:], 1.0, 0.0)

        df['positions'] = df['signal'].diff()
        
        if df['signal'][len(df)-1] == 1 and df['positions'][len(df)-1] == 1:
            return True
        else:
            return False

def run():
    for code, name in get_code_list():
        res = isMAGoldCross( code, 20, 60 )
        if res == True:
            print("MA20 MA60 GC {} {}".format(code,name))       
        

if __name__ == '__main__':
    run()