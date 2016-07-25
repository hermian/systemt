#-*- coding: utf-8 -*-

import win32com.client

from logger import get_logger
import win32com.client
from pywinauto import application
from pywinauto import timings
import time
import os
import sqlite3

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
    os.system("taskkill /im CpStart.exe")
    os.system("taskkill /im ncStarter.exe")

    app = application.Application()
    app.start("C:/DAISHIN/STARTER/ncStarter.exe /prj:cp")

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

def run():
    
    cp_restart()
    time.sleep(10)
    if isConnect() == True:
        get_logger().debug("cybos plus connected")
    else:
        get_logger().debug("cybos plus not connected")

if __name__ == '__main__':
    run()

