from napoleon.properties import AbstractObject, String


class AbstractVault(AbstractObject):

    pass


class AbstractPlateform(AbstractObject):

    pass


class AbstractCommandLine(AbstractObject):

    pass


class AbstractNamedObject(AbstractObject):

    name = String()


class AbstractTracer(AbstractNamedObject):

    pass


class AbstractClient(AbstractNamedObject):

    pass


class AbstractDatabase(AbstractNamedObject):

    pass


class AbstractInterface(AbstractNamedObject):

    pass


class AbstractDaemon(AbstractNamedObject):

    pass
