#-*- coding: utf-8 -*-

import win32com.client

from logger import get_logger
import win32com.client
from pywinauto import application
from pywinauto import timings
import time
import os
import sqlite3
from cp_constant import *

instCpTdUtil = win32com.client.Dispatch("CpTrade.CpTdUtil")

def isConnect():
    instCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    if instCpCybos.Isconnect == 1:
        return True
    else:
        return False

def get_password():
    with sqlite3.connect("pw.db") as con:
        cursor = con.cursor()
        pw1, pw2, pw3 = con.cursor().execute("SELECT PW1,PW2,PW3 FROM PW").fetchone()

    return pw1, pw2, pw3

def cp_restart():
    os.system("taskkill /im DibServer.exe")
    os.system("taskkill /im CpStart.exe")
    os.system("taskkill /im ncStarter.exe")
    time.sleep(3)

    app = application.Application()
    app.start("C:/DAISHIN/STARTER/ncStarter.exe /prj:cp")

    time.sleep(1)
    # security warn popup
    dlg = app.top_window_()
    btn_ctrl = dlg.Button0
    btn_ctrl.Click()
    time.sleep(1)
    
    title = "CYBOS Starter"
    dlg = timings.WaitUntilPasses(20, 0.5, lambda: app.window_(title=title))
    
    pw1, pw2, pw3 = get_password()

    pass_ctrl = dlg.Edit2
    pass_ctrl.SetFocus()
    pass_ctrl.TypeKeys(pw1)
    time.sleep(1)
    cert_ctrl = dlg.Edit3
    cert_ctrl.SetFocus()
    cert_ctrl.TypeKeys(pw2)
    time.sleep(1)

    btn_ctrl = dlg.Button0
    btn_ctrl.Click()


import threading
class autoPw(threading.Thread):
    def run(self):
        app = application.Application()
        title = "CybosPlus 주문확인 설정"
        dlg = timings.WaitUntilPasses(20, 0.5, lambda: app.window_(title=title))
    
        pw1, pw2, pw3 = get_password()
    
        pass_ctrl = dlg.Edit1
        pass_ctrl.SetFocus()
        pass_ctrl.TypeKeys(pw3)
    
        btn_ctrl = dlg.Button0
        btn_ctrl.Click()

def reboot():
    import os
    from time import sleep

    print ("GOING DOWN FOR A REBOOT IN 5 SECONDS")

    sleep (1)
    print ("5")
    sleep (1)
    print ("4")
    sleep (1)
    print ("3")
    sleep (1)
    print ("2")
    sleep (1)
    print ("1")
    sleep (1)
    print ("REBOOTING")
    os.system("shutdown -t 0 -r -f")


# 보유종목 매도기
# 이미 보유한 종목을 1% 수익으로 매도 주문을 넣는다.
def mystockseller():
    instCpTd6033 = win32com.client.Dispatch("CpTrade.CpTd6033")
    t = autoPw()        
    t.start()
    instCpTdUtil.TradeInit(0)
    acountnum = instCpTdUtil.AccountNumber
    instCpTd6033.SetInputValue(CPTD6033_PARAMETER_ACCOUNT_NUM, acountnum[0])
    instCpTd6033.SetInputValue(CPTD6033_PARAMETER_GOOD_CODE, CPTD6033_PARAMETER_GOOD_CODE_STOCK)
    instCpTd6033.BlockRequest()

    print("계좌명 %s"       % instCpTd6033.GetHeaderValue(CPTD6033_ACCOUNT_NAME))
    print("결제잔고 수량 %d" % instCpTd6033.GetHeaderValue(CPTD6033_PAYMENT_STOCK_COUNT))
    print("체결잔고 수량 %d" % instCpTd6033.GetHeaderValue(CPTD6033_CONCLUSION_STOCK_COUNT))
    print("평가금액 %d" % instCpTd6033.GetHeaderValue(CPTD6033_ASSESSED_VALUE))
    print("평가손인 %d" % instCpTd6033.GetHeaderValue(CPTD6033_VALUATION))
    print("수익율 %d" % instCpTd6033.GetHeaderValue(CPTD6033_REVENUE_RATIO))
    
    count = instCpTd6033.GetHeaderValue(CPTD6033_RECEIVE_COUNT)
    for i in range(0, count):
        print("종목명 %s" % instCpTd6033.GetDataValue(0, i))



# 백테스팅 결과 매수기
# 백테스팅 결과 종목을 현재가 -1%에 매수 주문을 넣는다.
# 잔고 / 매수 단위 금액 : 주문 종목 카운트
# 주문을 넣으면 order.db에 종목 코드를 저장 한다.
# 스키마 : code, name, price, volume, state(Order, Buyed) 
# order db에 이미 존재하는 종목은 skip 한다.
def buyFromBacktesting():
	pass

# 매수 이벤트가 발생하면 해당 종목을 +2%에 매도 주문을 넣는다.
# 매수가 체결 되자 마자 + 2%에 매도 주문을 넣는다.
# order.db를 업데이트 한다.
def sellByBuyEvent():
	pass

# 매도 이벤트가 발생하면 잔고 확인후 백테스팅 종목에 다음 순의 종목을 매수 한다.
# 매도된 종목은 oder.db에서 제거 한다.
def buyBySellEvent():
	buyFromBacktesting()
	pass
  

def run():
    
    if isConnect() == True:
        get_logger().debug("cybos plus connected")
        #cp_restart()
        #time.sleep(15)

        t = autoPw()        
        t.start()
        instCpTdUtil.TradeInit(0)
        acountnum = instCpTdUtil.AccountNumber
        print("{}".format(acountnum))

        mystockseller()
    else:
        get_logger().debug("cybos plus not connected")
        cp_restart()
        time.sleep(15)
        
        t = autoPw()        
        t.start()
        instCpTdUtil.TradeInit(0)
        acountnum = instCpTdUtil.AccountNumber
        print("{}".format(acountnum))

if __name__ == '__main__':
    run()

