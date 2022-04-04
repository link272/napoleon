import logging

from napoleon.properties.scalars import String
from napoleon.tools.singleton import Undefined


class Log(String):
    """Log alias"""

    def __init__(self,
                 default="root",
                 description=Undefined,
                 nullable=False
                 ):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)

    def __set__(self, instance, value):
        if isinstance(value, str):
            setattr(instance, self.private_name, value)
        elif isinstance(value, logging.Logger):
            setattr(instance, self.private_name, value.name)
        else:
            raise ValueError(f"{value} is not an instance of ({logging.Logger}, str)")

    def __get__(self, instance, owner=None):
        return logging.getLogger(getattr(instance, self.private_name))

    def to_primitive(self, value):
        return value.name

    def to_bytes(self, value):
        return value.name.encode()
