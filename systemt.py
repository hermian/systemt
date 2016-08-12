#-*- coding: utf-8 -*-
from time import sleep
from RepeatedTimer import RepeatedTimer
from cybosplus import *
from datetime import datetime

global running
running = False

def batch(msg):
    from time import localtime
    t = localtime()

    global running
    if running == True: 
        return

    # 03 reboot
    if t.tm_hour == 3 and t.tm_min == 0:
        running = True
        import cybosplus
        cybosplus.reboot()
        running = False

    # 08 cybos plus connect
    if t.tm_hour == 8 and t.tm_min == 0:
        running = True
        
        connect()
        running = False

    # 16 dataclawler
    if  t.tm_hour == 16 and t.tm_min == 0:
        running = True
        #import cybosplus
        #cybosplus.run()
        import datacrawler
        datacrawler.run()
        import analyze
        analyze.run()
        import backtesting
        backtesting.run()
        running = False

# batch process
if __name__ == '__main__':
    """
    print ("starting...")
    rt = RepeatedTimer(10, batch, "batch") # it auto-starts, no need of rt.start()
    try:
        sleep(60*60*24) # your long-running job goes here...
    finally:
        rt.stop() # better in a try/finally block to make sure the program ends!
    """
    if datetime.now().date().weekday() == 5 or datetime.now().date().weekday() == 6:
        exit() 
    else:    
        import datacrawler
        datacrawler.run()
        import analyze
        analyze.run()
        import backtesting
        backtesting.run()
   
