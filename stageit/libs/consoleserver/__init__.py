class BaseConsoleServer():
    def __init__(self, hostname, username, password, transport, line, **kwargs):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.transport = transport
        self.line = line
    
    def reset(self):
        pass