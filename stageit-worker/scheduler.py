import time
import schedule
import os
import threading
import logging
from requests import get
from libs.base_worker import BaseWorker
from libs.fake_worker import FakeWorker

LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
logging.basicConfig(level=LOGLEVEL)

worker_name = os.environ['WORKER_ID']
stageit_endpoint = os.environ['STAGEIT_ENDPOINT']
token = os.environ['TOKEN']
history_url = stageit_endpoint + "/api/history/?format=json&search=Queued"
headers={'Authorization': f'Token {token}'}

def check_tasks():
    try:
        history_list = get(history_url, headers=headers)
    except:
        pass

    if len(history_list.json()) == 0:
        print("Nothing")
        return True

    for history in history_list.json():
        if history['status'] == 'Queued':
            job_thread = threading.Thread(target=run_threaded, args=(history,))
            job_thread.start()


def run_threaded(history):
    BaseWorker(historydata=history, endpoint=stageit_endpoint, worker_id=worker_pkid, headers=headers)

workerlistplain = get(f'{stageit_endpoint}/api/remoteworker/?name={worker_name}', headers=headers)
workerlist = workerlistplain.json()

worker_pkid = workerlist[0]['pkid']
print(worker_pkid)

schedule.every(10).seconds.do(check_tasks)

while 1:
    schedule.run_pending()
    time.sleep(1)