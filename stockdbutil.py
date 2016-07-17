#-*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import sqlite3

import numpy as np

from logger import get_logger

from datetime import datetime

def _checkData( cursor, table_name ):
    row = cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)).fetchone()
    if row is None: return False
        
    row = cursor.execute("SELECT COUNT(*) FROM '{}'".format(table_name)).fetchone()
    if row is None : return False

    return True

def makeDataFrame( code ):
    with sqlite3.connect("price.db") as con:
        cursor = con.cursor()
        table_name = code
        
        if _checkData( cursor, table_name ) == False: 
            price_data = {'DATE':[],
                          'OPEN':[],
                          'HIGH':[],
                          'LOW':[],
                          'CLOSE':[],
                          'VOLUME':[]}
            df = DataFrame(price_data)
            return df
             
        else:
            df = pd.read_sql("SELECT * FROM '{}'".format(table_name), con, index_col=None)
            return df

def get_last_update_date( table_name ):
    with sqlite3.connect("price.db") as con:
        cursor = con.cursor()
        row = cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)).fetchone()
        if row is None: return None

        row = cursor.execute("SELECT MAX(Date) FROM '{}'".format(table_name)).fetchone()
        return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')

def get_first_update_date( table_name ):
    with sqlite3.connect("price.db") as con:
        cursor = con.cursor()
        row = cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)).fetchone()
        if row is None: return None

        row = cursor.execute("SELECT MIN(Date) FROM '{}'".format(table_name)).fetchone()
        return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')