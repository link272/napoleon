from napoleon.properties import AbstractObject, String, Instance


class BaseClient(AbstractObject):

    name = String()


class BaseInterface(AbstractObject):

    name = String()
    client = Instance(BaseClient)


class BaseAuthentication(AbstractObject): pass
