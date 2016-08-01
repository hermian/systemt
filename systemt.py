#-*- coding: utf-8 -*-
from time import sleep
from RepeatedTimer import RepeatedTimer

def hello(name):
    print ("Hello %s!" % name)

print ("starting...")
rt = RepeatedTimer(1, hello, "World") # it auto-starts, no need of rt.start()
try:
    sleep(60*60*24) # your long-running job goes here...
finally:
    rt.stop() # better in a try/finally block to make sure the program ends!