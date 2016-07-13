#-*- coding: utf-8 -*-

from datetime import datetime
from datetime import timedelta
import sqlite3

from pandas import Series, DataFrame

from logger import get_logger
from stockcode import get_code_list
from settings import START_DATE
from cp_constant import *
import win32com.client

def run():
    with sqlite3.connect("price.db") as con:
        cursor = con.cursor()

        def _make_long_date(date):
            return date.year * 10000 + date.month * 100 + date.day

        def _get_recent_date(cursor, table_name):
            row = cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='{}'".format(table_name)).fetchone()
            if row is None: return None

            row = cursor.execute("SELECT MAX(Date) FROM '{}'".format(table_name)).fetchone()
            return datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')

        for code, name in get_code_list():

            table_name = code
            
            recent_date = _get_recent_date(cursor, table_name)
            if recent_date is None: recent_date = START_DATE

            if recent_date.date() == datetime.now().date(): continue

            if recent_date.weekday() == 4 and datetime.now() - recent_date < timedelta(hours=64): continue

            start_date = (recent_date + timedelta(days=1))
            end_date = datetime.now()

            if datetime.now().hour < 16: end_date = datetime.now() - timedelta(days=1)

            if start_date > end_date: continue

            instStockChart = win32com.client.Dispatch("CpSysDib.StockChart")

            instStockChart.SetInputValue(CPSTOCKCHART_REQ_CODE, code)
            instStockChart.SetInputValue(CPSTOCKCHART_REQ_DATE_OR_COUNT, CPSTOCKCHART_REQ_PARAM_DATE)

            instStockChart.SetInputValue(CPSTOCKCHART_REQ_END_DATE,_make_long_date(end_date))
            instStockChart.SetInputValue(CPSTOCKCHART_REQ_START_DATE,_make_long_date(start_date))

            instStockChart.SetInputValue(CPSTOCKCHART_REQ_FIELD, 
                                            [CPSTOCKCHART_REQ_PARAM_FIELD_DATE,
                                            CPSTOCKCHART_REQ_PARAM_FIELD_OPEN,
                                            CPSTOCKCHART_REQ_PARAM_FIELD_HIGH,
                                            CPSTOCKCHART_REQ_PARAM_FIELD_LOW,
                                            CPSTOCKCHART_REQ_PARAM_FIELD_CLOSE,
                                            CPSTOCKCHART_REQ_PARAM_FIELD_VOLUME])
            instStockChart.SetInputValue(CPSTOCKCHART_REQ_TYPE, CPSTOCKCHART_REQ_TYPE_PARAM_DAY)
            instStockChart.SetInputValue(CPSTOCKCHART_REQ_ADJ, CPSTOCKCHART_REQ_ADJ_PARAM_ADJUST)

            instStockChart.BlockRequest()

            numData = instStockChart.GetHeaderValue(CPSTOCKCHART_RES_DATA_COUNT)
            price_data = {'DATE':[],
                          'OPEN':[],
                          'HIGH':[],
                          'LOW':[],
                          'CLOSE':[],
                          'VOLUME':[]}

            # cybos plus 최근데이터 부터 온다
            for i in reversed(range(numData)):
                
                long_date = instStockChart.GetDataValue(0, i)
                year = int(long_date / 10000)
                month = int(long_date / 100) % 100
                day = long_date % 100
                dateval = datetime(year, month, day, 0, 0, 0)

                open = instStockChart.GetDataValue(1, i)
                high = instStockChart.GetDataValue(2, i)
                low = instStockChart.GetDataValue(3, i)
                close = instStockChart.GetDataValue(4, i)
                volume = instStockChart.GetDataValue(5, i)

                price_data['DATE'].append(dateval)
                price_data['OPEN'].append(open)
                price_data['HIGH'].append(high)
                price_data['LOW'].append(low)
                price_data['CLOSE'].append(close)
                price_data['VOLUME'].append(volume)

            price = DataFrame(price_data)
            price.to_sql(table_name, con, if_exists='append', chunksize=1000)
            get_logger().debug("{} 종목의 {}데이터를 저장 하였습니다.".format(code, len(price)))

            #remove old data
            row = cursor.execute("SELECT COUNT(*) FROM '{}'".format(table_name)).fetchone()
            if row[0] > 2000:
                row = cursor.execute("DELETE FROM '{}' WHERE DATE = (SELECT MIN(DATE) FROM '{}')".format(table_name, table_name))
            
if __name__ == '__main__':
    run()

