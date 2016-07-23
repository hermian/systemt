#-*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import sqlite3

import numpy as np

from logger import get_logger
from stockcode import get_code_list
from analyze import get_code_list_from_analyze

from stockdbutil import makeDataFrame, get_per_bps_with_code, get_last_data_with_code
from stockdbutil import get_first_update_date, get_last_update_date

from zipline.algorithm import TradingAlgorithm
from zipline.api import history, order_target, symbol, order, record, add_history
from zipline.api import set_commission, commission
from settings import COMMISSION, SELL_PRICE_RATIO, STRATEGY

import talib as ta

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
    if len(data) > len(df):
        data = data[len(data) - len(df):]
    else:
        df = df[len(df) - len(data):]

    data[code] = np.where(1, df['CLOSE'], df['CLOSE'])    
    
    return data

#MAGC
def initialize_magc(context):
    set_commission(commission.PerDollar(cost = COMMISSION))
    add_history(20, '1d', 'price')
    add_history(60, '1d', 'price')
    context.i = 0
    context.investment = False
    context.buy_price = 0

def handle_data_magc(context, data):
    context.i += 1
    if context.i < 60:
        return

    ma20 = history(20, '1d', 'price').mean()
    ma60 = history(60, '1d', 'price').mean()

    buy = False
    sell = False

    sym = symbol(code)

    count = int(100000 /  data[sym].price)
    
    if context.investment == False:
        if ma20[sym] > ma60[sym] :
            order_target(sym, count)
            context.investment = True
            context.buy_price = data[sym].price
            buy = True
    else:
        if (data[sym].price > context.buy_price + (context.buy_price * sell_point)):
            order_target(sym, -count)
            context.investment = False
            sell = True
            
    record(code=data[sym].price, ma20=ma20[sym], ma60=ma60[sym], buy=buy, sell=sell)
    
#MACD
# Define the MACD function  
def MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9):  
    '''  
    Function to return the difference between the most recent  
    MACD value and MACD signal. Positive values are long  
    position entry signals 

    optional args:  
        fastperiod = 12  
        slowperiod = 26  
        signalperiod = 9

    Returns: macd - signal  
    '''  
    macd, signal, hist = ta.MACD(prices.values,  
                                 fastperiod=fastperiod,  
                                 slowperiod=slowperiod,  
                                 signalperiod=signalperiod)  
    return macd[-1] - signal[-1]

def initialize_macd(context):
    set_commission(commission.PerDollar(cost = COMMISSION))
    context.i = 0
    context.investment = False
    context.buy_price = 0
    context.position = 0.0
    add_history(40, '1d', 'price')

def handle_data_macd(context, data):
    context.i += 1
    if context.i < 60:
        return

    buy = False
    sell = False

    sym = symbol(code)

    count = int(100000 /  data[sym].price)

    prices = history(40, '1d', 'price')
    macd = prices.apply(MACD, fastperiod=12, slowperiod=26, signalperiod=9)
 
    if context.investment == False:
        if macd[sym] > 0 and context.position == -1:
            order_target(sym, count)
            context.investment = True
            context.buy_price = data[sym].price
            buy = True
            context.position = 1
    else:
        if (data[sym].price > context.buy_price + (context.buy_price * sell_point)):
            order_target(sym, -count)
            context.investment = False
            sell = True

    if macd[sym] < 0 :
        context.position = -1
    
    if macd[sym] > 0 :
        context.position = 1
            
    record(code=data[sym].price, macd=macd[sym], buy=buy, sell=sell)
    

def initialize_bband(context):
    set_commission(commission.PerDollar(cost = COMMISSION))
    context.i = 0
    context.investment = False
    context.buy_price = 0
    context.position = 0.0
    add_history(20, '1d', 'price')

def handle_data_bband(context, data):
    context.i += 1
    if context.i < 20:
        return

    buy = False
    sell = False

    sym = symbol(code)

    count = int(100000 /  data[sym].price)

    prices = history(20, '1d', 'price')
    upper, middle, lower = ta.BBANDS(
        prices[sym].values,
        timeperiod=20,
        nbdevup=2,
        nbdevdn=2,
        matype=0)
 
    if context.investment == False:
        if lower[-1] > data[sym].price:
            order_target(sym, count)
            context.investment = True
            context.buy_price = data[sym].price
            buy = True
            context.position = 1
    else:
        if (data[sym].price > context.buy_price + (context.buy_price * sell_point)):
            order_target(sym, -count)
            context.investment = False
            sell = True
            
    record(code=data[sym].price, upper=upper[-1], lower=lower[-1], makeBacktestingDataFrame=middle[-1], buy=buy, sell=sell)

def run():
    global code
    global sell_point

    with sqlite3.connect("backtesting.db") as con:
        cursor = con.cursor()
        
        backtesting_save_data = { 'CODE':[],
                                  'NAME':[],
                                  'STRATEGY':[],
                                  'SELL_PRICE_RATIO':[],
                                  'PORTFOLIO_VALUE':[],
                                  'OPEN':[],
                                  'HIGH':[],
                                  'LOW':[],
                                  'CLOSE':[],
                                  'VOLUME':[],
                                  'PER':[],
                                  'BPS':[],
                                  'PBR':[]}

        for strategys in STRATEGY:
            for code, name in get_code_list_from_analyze(strategys):
                per , bps = get_per_bps_with_code(code)

                open, high, low, close, volume = get_last_data_with_code(code)
                if bps != 0:
                    pbr = close / bps
                else:
                    pbr = 0.0

                get_logger().debug("code : {}. name:{} strategy:{} start".format(code,name,strategys))
                for point in SELL_PRICE_RATIO:
                    sell_point = point
                    data = makeBacktestingDataFrame(code)
                    if strategys == 'MAGC':
                        algo = TradingAlgorithm(capital_base=10000000, initialize=initialize_magc, handle_data=handle_data_magc, identifiers=[code]  )
                        results = algo.run(data)
                    elif strategys == 'MACD':
                        algo = TradingAlgorithm(capital_base=10000000, initialize=initialize_macd, handle_data=handle_data_macd, identifiers=[code]  )
                        results = algo.run(data)
                    elif strategys == 'BBAND':
                        algo = TradingAlgorithm(capital_base=10000000, initialize=initialize_bband, handle_data=handle_data_bband, identifiers=[code]  )
                        results = algo.run(data)

                    backtesting_save_data['CODE'].append(code)
                    backtesting_save_data['NAME'].append(name)
                    backtesting_save_data['STRATEGY'].append(strategys)
                    backtesting_save_data['SELL_PRICE_RATIO'].append('{}'.format(point))
                    backtesting_save_data['PORTFOLIO_VALUE'].append(results['portfolio_value'][-1])
                    backtesting_save_data['OPEN'].append(open)
                    backtesting_save_data['HIGH'].append(high)
                    backtesting_save_data['LOW'].append(low)
                    backtesting_save_data['CLOSE'].append(close)
                    backtesting_save_data['VOLUME'].append(volume)
                    backtesting_save_data['PER'].append(per)
                    backtesting_save_data['BPS'].append(bps)
                    backtesting_save_data['PBR'].append(pbr)

                    backtesting_save_df = DataFrame(backtesting_save_data)
               
                backtesting_save_df.to_sql('BACK', con, if_exists='replace', chunksize=1000)
                    #print(results[['starting_cash', 'ending_cash', 'ending_value', 'portfolio_value']])
                get_logger().debug("code : {}. name:{} strategy:{} end".format(code,name,strategys))
if __name__ == '__main__':
    run()