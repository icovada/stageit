broker_url = 'amqp://'
result_backend = 'amqp://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Rome'
enable_utc = True

imports = ("stageit.libs.fake_worker", )