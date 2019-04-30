"""
Provide methods to reset the serial connection

To be expanded by platform-specific modules
"""

class BaseConsoleServer():
    """Base class"""
    def __init__(self, hostname, username, password, transport, line, **kwargs):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.transport = transport
        self.line = line

    def reset(self):
        """Expand me"""
        raise NotImplementedError
