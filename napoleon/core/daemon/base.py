from napoleon.properties import AbstractObject, String


class BaseDaemon(AbstractObject):
    """A base class for threads running as daemon"""

    name = String()

    def start(self):
        raise NotImplementedError

    @property
    def is_active(self):
        raise NotImplementedError

    def __del__(self):
        self.shutdown()
        super().__del__()

    def shutdown(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError
