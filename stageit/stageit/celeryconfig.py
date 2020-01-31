import os

broker_url = os.environ.get("broker_url"),

task_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Rome'
enable_utc = True

imports = ("stageit.libs.fake_worker",
           "stageit.libs.base_worker", )
