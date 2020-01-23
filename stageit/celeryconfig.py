broker_url = 'amqp://rabbit'

task_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Rome'
enable_utc = True

imports = ("stageit.libs.fake_worker",
           "stageit.libs.base_worker", )
