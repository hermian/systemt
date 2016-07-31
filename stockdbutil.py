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

def get_per_bps_with_code(code):
    with sqlite3.connect("code.db") as con:
        for per, bps in con.cursor().execute("SELECT PER, BPS FROM CODE WHERE CODE = '{}'".format(code)):
            per = per
            bps = bps

    return per, bps

def get_industry_with_code(code):
    with sqlite3.connect("code.db") as con:
        for industry_code, industry_name in con.cursor().execute("SELECT INDUSTRY_CODE, INDUSTRY FROM CODE WHERE CODE = '{}'".format(code)):
            industry_code = industry_code
            industry_name = industry_name

    return industry_code, industry_name


def get_last_data_with_code(code):
    with sqlite3.connect("price.db") as con:
        for open, high, low, close, volume in con.cursor().execute("SELECT OPEN, HIGH, LOW, CLOSE, VOLUME FROM '{}' WHERE DATE = (SELECT MAX(DATE) FROM '{}')".format(code, code)):
            open = open
            high = high
            low = low
            close = close
            volume = volume

    return open, high, low, close, volume

