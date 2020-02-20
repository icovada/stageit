import time
import schedule
import requests

def check_tasks():
    pass

schedule.every(10).seconds.do(check_tasks)

while 1:
    schedule.run_pending()
    time.sleep(1)