import time
import schedule
import os
from requests import get
from libs.base_device import base_device
from libs.fake_device import fake_device

worker_id = os.environ['WORKER_ID']
stageit_endpoint = os.environ['STAGEIT_ENDPOINT']
token = os.environ['TOKEN']
history_url = stageit_endpoint + "/api/history/?format=json&search=Queued"

def check_tasks():
    try:
        history_list = get(history_url)
    except:
        pass

    if len(history_list) == 0:
        return True

    for history in history_list:
        if history['status'] == 'Queued' and history['fkremoteworker'] == worker_id:
            fake_device()



my_pkid = get(stageit_endpoint + "/?name=" + worker_id)

schedule.every(10).seconds.do(check_tasks)

while 1:
    schedule.run_pending()
    time.sleep(1)