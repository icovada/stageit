broker_url = 'amqp://'
result_backend = 'amqp://'

task_serializer = 'pickle'
result_serializer = 'pickle'
accept_content = ['pickle']
timezone = 'Europe/Rome'
enable_utc = True

imports = ("stageit.libs.fake_worker", 
           "stageit.libs.base_worker", )