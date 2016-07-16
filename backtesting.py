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
    """
        대신 증권으로 만든 데이터를 쓰면 zipline에서 예외가 발생한다.
        날짜 인덱스를 임의 로 set_index('DATE')로 해주어도 트레이딩 day index의 문제가 있는 것으로 보인다.
        다음의 절차로 처리 한다.
        먼저 padnas_datareader로 야후에서 DB에 있는 시작 날짜와 끝날짜의 데이터를 가져 온다. (삼성전자 같은 걸로)
        DB에서 가져온 현재 코드의 price 종가 부분만 을 취해서
        pandas 로 가져온 날짜 인덱스에 값을 쓴다.

     data = data[len(data) - len(df):]
        
    """
    import pandas_datareader.data as web
    import datetime
    start = datetime.datetime(2010, 1, 1)
    end = datetime.datetime(2016,7,15)
    data  = web.DataReader("AAPL", "yahoo", start, end)
    data = data[['Adj Close']]
    data.columns = [code]
    data.head()
    data = data.tz_localize("UTC")

    df = makeDataFrame(code)
    
    
    df = df[['CLOSE']]
    data = data[len(data) - len(df):]
    data[code] = np.where(1, df['CLOSE'], df['CLOSE'])    
    
    return data

def initialize(context):
    add_history(5, '1d', 'price')
    add_history(20, '1d', 'price')
    context.i = 0
    

def handle_data(context, data):
    context.i += 1
    if context.i < 20:
        return

    ma5 = history(5, '1d', 'price').mean()
    ma20 = history(20, '1d', 'price').mean()

    sym = symbol('A059090')
    if ma5[sym] > ma20[sym]:
        order(sym, 1)
    else:
        order(sym, -1)
    
    record(AAPL=data[sym].price, ma5=ma5[sym], ma20=ma20[sym])



def run():
    data = makeBacktestingDataFrame('A059090')
    """
    import pandas_datareader.data as web
    import datetime
    start = datetime.datetime(2016, 1, 1)
    end = datetime.datetime(2016,7,15)
    data  = web.DataReader("005930.KS", "yahoo", start, end)
    data = data[['Adj Close']]
    data.columns = ["AAPL"]
    data.head()
    data = data.tz_localize("UTC")
    """

    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, identifiers=['A059090']  )
    results = algo.run(data)
    
    print(results[['starting_cash', 'ending_cash', 'ending_value', 'portfolio_value']])


if __name__ == '__main__':
    run()