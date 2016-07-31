#-*- coding: utf-8 -*-

import pandas as pd
from pandas import Series, DataFrame
import sqlite3

import numpy as np

from logger import get_logger
from stockcode import get_code_list

from stockdbutil import makeDataFrame, get_per_bps_with_code, get_last_data_with_code

def isMAGoldCross( df, MA1 = 20, MA2 = 60 ):
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

def isBBandSignal( df, period = 20):
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

def isMACDSignal( df, n1 = 12, n2= 26, c= 9):
    df['MACD'] = pd.ewma(df['CLOSE'], span=n1) - pd.ewma(df['CLOSE'], span=n2)
    df['MACD_Signal'] = pd.ewma(df['MACD'], span=c)
    df['signal'] = 0.0
    df['signal'] = np.where(df['MACD'] > df['MACD_Signal'], 1.0, 0.0)
    df['positions'] = 0.0
    df['positions'] = df['signal'].diff()

    if df['signal'][len(df)-1] == 1 and df['positions'][len(df)-1] == 1:
        return True
    else:
        return False

def get_code_list_from_analyze( type ):
    result = dict()
    with sqlite3.connect("analyze.db") as con:
        for code, name in con.cursor().execute("SELECT code, name FROM '{}'".format(type)):
            result[code] = name

    return result.items()

def run():
    with sqlite3.connect("analyze.db") as con:
        cursor = con.cursor()

        code_magc = {'CODE':[],
                     'NAME':[]}
        code_bband= {'CODE':[],
                     'NAME':[]}
        code_macd = {'CODE':[],
                     'NAME':[]}

        per_bps_pbr = {'CODE':[],
                       'NAME':[],
                       'OPEN':[],
                       'HIGH':[],
                       'LOW':[],
                       'CLOSE':[],
                       'VOLUME':[],
                       'PER':[],
                       'BPS':[],
                       'PBR':[]}

        for code, name in get_code_list():
            df = makeDataFrame( code )
            if len(df) == 0: continue

            res = isMAGoldCross( df, 20, 60 )
            if res == True:
                code_magc['CODE'].append(code)
                code_magc['NAME'].append(name)
                get_logger().debug("MA20, MA60 Golden Cross {}{}".format(code,name))

            res = isBBandSignal( df, 20 )
            if res == True:
                code_bband['CODE'].append(code)
                code_bband['NAME'].append(name)
                get_logger().debug("BBnad lower after up {}{}".format(code,name))

            res = isMACDSignal( df, 12, 26, 9)
            if res == True:
                code_macd['CODE'].append(code)
                code_macd['NAME'].append(name)
                get_logger().debug("MACD sig {}{}".format(code,name))

            # per,bps, pbr table
            per , bps = get_per_bps_with_code(code)
            open, high, low, close, volume = get_last_data_with_code(code)
            if bps != 0:
                pbr = close / bps
            else:
                pbr = 0.0

            per_bps_pbr['CODE'].append(code)
            per_bps_pbr['NAME'].append(name)
            per_bps_pbr['OPEN'].append(open)
            per_bps_pbr['HIGH'].append(high)
            per_bps_pbr['LOW'].append(low)
            per_bps_pbr['CLOSE'].append(close)
            per_bps_pbr['VOLUME'].append(volume)
            per_bps_pbr['PER'].append(per)
            per_bps_pbr['BPS'].append(bps)
            per_bps_pbr['PBR'].append(pbr)
            get_logger().debug("{} {} {} {} {} {} {} {} {} {}".format(code,name,open,high,low, close,volume,per,bps,pbr))

        magc = DataFrame(code_magc)
        bband   = DataFrame(code_bband)
        macd = DataFrame(code_macd)
        magc.to_sql("MAGC", con, if_exists='replace', chunksize=1000)
        get_logger().debug("MAGC {} saved.".format(len(magc)))
        bband.to_sql("BBAND", con, if_exists='replace', chunksize=1000)
        get_logger().debug("BBAND {} saved.".format(len(bband)))
        macd.to_sql("MACD", con, if_exists='replace', chunksize=1000)
        get_logger().debug("MACD {} saved.".format(len(macd)))

        per_bps_pbr_df = DataFrame(per_bps_pbr)
        per_bps_pbr_df.to_sql("BPS", con, if_exists='replace', chunksize=1000)
        get_logger().debug("BPS {} saved.".format(len(per_bps_pbr_df)))

if __name__ == '__main__':
    run()

"""
select code, name from 
	( select * from 
		(select code, name, close, volume, per, bps, pbr from 
			bps order by volume desc) 
		order by per)
	where pbr < 1 and bps > 0
	order by pbr ;


"""