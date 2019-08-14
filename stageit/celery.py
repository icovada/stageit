from celery import Celery
import os

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery()
app.config_from_object('stageit.celeryconfig')

@app.task
def test():
    print("Hello")

if __name__ == "__main__":
    app.start()