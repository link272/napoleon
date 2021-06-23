from napoleon.properties import AbstractObject, String


class AbstractVault(AbstractObject):

    def decrypt(self, data):
        raise NotImplementedError

    def encrypt(self, data):
        raise NotImplementedError


class AbstractPlatform(AbstractObject):

    @classmethod
    def from_platform(cls):
        raise NotImplementedError


class AbstractCommandLine(AbstractObject):

    @classmethod
    def from_cmd(cls, add_help=False):
        raise NotImplementedError


class AbstractNamedObject(AbstractObject):

    name = String()

    def __str__(self):
        return self.name


class AbstractSharedInterface(AbstractNamedObject):

    pass


class AbstractTracer(AbstractNamedObject):

    pass


class AbstractClient(AbstractNamedObject):

    pass


class AbstractDatabase(AbstractNamedObject):

    pass


class AbstractDaemon(AbstractNamedObject):

    pass
