#-*- coding: utf-8 -*-

import win32com.client

from logger import get_logger
import win32com.client
from pywinauto import application
from pywinauto import timings
import time
import os
import sqlite3

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

def run():
    
    if isConnect() == True:
        get_logger().debug("cybos plus connected")
        cp_restart()
        time.sleep(15)

        t = autoPw()        
        t.start()
        instCpTdUtil.TradeInit(0)
        acountnum = instCpTdUtil.AccountNumber
        print("{}".format(acountnum))
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

