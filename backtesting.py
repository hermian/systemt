#-*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import sqlite3

import numpy as np

from logger import get_logger
from stockcode import get_code_list
from analyze import get_code_list_from_analyze

from stockdbutil import makeDataFrame
from stockdbutil import get_first_update_date, get_last_update_date

from zipline.algorithm import TradingAlgorithm
from zipline.api import history, order_target, symbol, order, record, add_history

def makeBacktestingDataFrame( code ):
    """
        대신 증권으로 만든 데이터를 쓰면 zipline에서 예외가 발생한다.
        날짜 인덱스를 임의 로 set_index('DATE')로 해주어도 트레이딩 day index의 문제가 있는 것으로 보인다.
        다음의 절차로 처리 한다.
        먼저 padnas_datareader로 야후에서 DB에 있는 시작 날짜와 끝날짜의 데이터를 가져 온다. (삼성전자 같은 걸로)
        DB에서 가져온 현재 코드의 price 종가 부분만 을 취해서
        pandas 로 가져온 날짜 인덱스에 값을 쓴다.
    """
    import pandas_datareader.data as web
    start = get_first_update_date(code)
    end = get_last_update_date(code)

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
    add_history(20, '1d', 'price')
    add_history(60, '1d', 'price')
    context.i = 0
    context.investment = False
    context.buy_price = 0
    

def handle_data(context, data):
    context.i += 1
    if context.i < 60:
        return

    ma20 = history(20, '1d', 'price').mean()
    ma60 = history(60, '1d', 'price').mean()

    buy = False
    sell = False

    sym = symbol(code)
    
    if context.investment == False:
        if ma20[sym] > ma60[sym] :
            order_target(sym, 100)
            context.investment = True
            context.buy_price = data[sym].price
            buy = True
    else:
        if (data[sym].price > context.buy_price + (context.buy_price * 0.01)):
            order_target(sym, -100)
            context.investment = False
            sell = True
            
    record(code=data[sym].price, ma20=ma20[sym], ma60=ma60[sym], buy=buy, sell=sell)
    
    """
        1%, 2%, 3%, 4%, 5% sell
    """
    
    

def run():
    global code
    code = 'A059090'
    data = makeBacktestingDataFrame(code)
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data, identifiers=[code]  )
    results = algo.run(data)
    
    print(results[['starting_cash', 'ending_cash', 'ending_value', 'portfolio_value']])

if __name__ == '__main__':
    run()