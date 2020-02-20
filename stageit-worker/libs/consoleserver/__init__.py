"""
Provide methods to reset the serial connection

To be expanded by platform-specific modules
"""

class BaseConsoleServer():
    """Base class"""
    def __init__(self, **kwargs):
        self.hostname = kwargs.get('hostname')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.transport = kwargs.get('transport')
        self.line = kwargs.get('line')

    def reset(self):
        """Expand me"""
        raise NotImplementedError
