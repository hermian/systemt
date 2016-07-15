#-*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import sqlite3

import numpy as np

from logger import get_logger
from stockcode import get_code_list

from stockdata import makeDataFrame

from zipline.algorithm import TradingAlgorithm
from zipline.api import history, order_target, symbol, order, record, add_history

#A059090

def makeBacktestingDataFrame( code ):
    df = makeDataFrame(code)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df = df[['DATE','CLOSE']]
    df = df.set_index('DATE')
    df = df.tz_localize("UTC")
    
    df.columns = [code]
    return df

def initialize(context):
    pass
    

def handle_data(context, data):
    order(symbol('A059090'),1)


def run():
    data = makeBacktestingDataFrame('A059090')
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, identifiers=['A059090']  )
    results = algo.run(data)
    print(results)


if __name__ == '__main__':
    run()