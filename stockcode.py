#-*- coding: utf-8 -*-
import requests
import sqlite3

import win32com.client
from time import sleep
from logger import get_logger

from cp_constant import *
from pandas import Series, DataFrame

def insert_from_cp(con):
    instCpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")
    instStockMst = win32com.client.Dispatch("dscbo1.StockMst")
    code_data = {'CODE':[],
                 'NAME':[],
                 'TYPE':[]}

    for i in range(0, instCpStockCode.GetCount()):
        code = instCpStockCode.GetData(CPSTOCKCODE_CODE, i)
        name = instCpStockCode.GetData(CPSTOCKCODE_NAME, i)
        code_data['CODE'].append(code)
        code_data['NAME'].append(name)
        
        instStockMst.SetInputValue(0, code)
        instStockMst.BlockRequest()
        type = instStockMst.GetHeaderValue(CPSTOCKMST_CATEGORY)

        code_data['TYPE'].append(type)

    data = DataFrame(code_data)
    data.to_sql("CODE", con, if_exists='replace', chunksize=1000)
    get_logger().debug("{} 주식 종목 코드를 저장 하였습니다.".format(len(data)))

def get_code_list():
    result = dict()
    with sqlite3.connect("code.db") as con:
        for code, name in con.cursor().execute("SELECT code, name FROM CODE"):
            result[code] = name

    return result.items()

def run():
    with sqlite3.connect("code.db") as con:
        cursor = con.cursor()
        insert_from_cp(con)

if __name__ == '__main__':
    run()


