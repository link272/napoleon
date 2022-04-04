import base64
import decimal
import json
import uuid

import pendulum

from .base import Property
from ..tools.singleton import Undefined


class Scalar(Property):  # noqa

    __slots__ = ()

    def to_primitive(self, value):
        raise NotImplementedError

    def from_primitive(self, value):
        raise NotImplementedError

    def to_bytes(self, value):
        raise NotImplementedError


class Boolean(Scalar):

    __slots__ = ()

    def __init__(self,
                 *,
                 default=False,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)

    def to_primitive(self, value):
        return bool(value)

    def from_primitive(self, value):
        return bool(value)

    def to_bytes(self, value):
        return str(value).encode()

    @property
    def type(self):
        return bool


class Float(Scalar):

    __slots__ = ("minimum", "maximum", "exclusive_minimum", "exclusive_maximum", "multiple_of",)

    def __init__(self,
                 default=0.,
                 minimum=Undefined,
                 maximum=Undefined,
                 exclusive_minimum=Undefined,
                 exclusive_maximum=Undefined,
                 multiple_of=Undefined,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.minimum = minimum
        self.maximum = maximum
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.multiple_of = multiple_of

    def to_primitive(self, value):
        return float(value)

    def from_primitive(self, value):
        return float(value)

    def to_bytes(self, value):
        return value.hex().encode()

    @property
    def type(self):
        return float


class Integer(Scalar):

    __slots__ = ("minimum", "maximum", "exclusive_minimum", "exclusive_maximum", "multiple_of",)

    def __init__(self,
                 default=0,
                 minimum=Undefined,
                 maximum=Undefined,
                 exclusive_minimum=Undefined,
                 exclusive_maximum=Undefined,
                 multiple_of=Undefined,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.minimum = minimum
        self.maximum = maximum
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.multiple_of = multiple_of

    def to_primitive(self, value):
        return int(value)

    def from_primitive(self, value):
        return int(value)

    def to_bytes(self, value):
        return str(value).encode()

    @property
    def type(self):
        return int


class String(Scalar):

    __slots__ = ("min_length", "max_length", "enum", "pattern", "format")

    def __init__(self,
                 default="",
                 enum=Undefined,
                 min_length=Undefined,
                 max_length=Undefined,
                 pattern=Undefined,
                 format=Undefined,  # noqa
                 description=Undefined,
                 nullable=True
                 ):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.min_length = min_length
        self.max_length = max_length
        self.enum = enum
        self.pattern = pattern
        self.format = format

    def to_primitive(self, value):
        return str(value)

    def from_primitive(self, value):
        return str(value)

    @classmethod
    def as_constant(cls, default):
        return cls(default=default, enum=[default])

    def to_bytes(self, value):
        return str(value).encode()

    @property
    def type(self):
        return str


class Decimal(Scalar):

    def __init__(self,
                 default=decimal.Decimal(),
                 minimum=Undefined,
                 maximum=Undefined,
                 exclusive_minimum=Undefined,
                 exclusive_maximum=Undefined,
                 multiple_of=Undefined,
                 description=Undefined,
                 nullable=True):
        _default = decimal.Decimal(default) if isinstance(default, (int, str, float)) else default
        super().__init__(default=_default,
                         description=description,
                         nullable=nullable)
        self.minimum = minimum
        self.maximum = maximum
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.multiple_of = multiple_of

    def from_primitive(self, value):  # noqa
        return decimal.Decimal(value)

    def to_primitive(self, value):  # noqa
        return str(value)

    def to_bytes(self, value):
        return str(value).encode()

    @property
    def type(self):
        return decimal.Decimal


class Bytes(Scalar):

    __slots__ = ()

    def __init__(self,
                 *,
                 default=None,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)

    def to_primitive(self, value):
        return base64.urlsafe_b64encode(value)

    def from_primitive(self, value):
        return base64.urlsafe_b64decode(value)

    @property
    def type(self):
        return bytes

    def to_bytes(self, value):
        return value


class JSON(Scalar):

    __slots__ = ()

    def __init__(self,
                 *,
                 default=dict,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)

    def to_bytes(self, value):
        return json.dumps(value, sort_keys=True).encode()

    def from_primitive(self, value):
        return json.loads(value)

    def to_primitive(self, value):
        return json.dumps(value)

    @property
    def type(self):
        return dict


class DateTime(Scalar):

    __slots__ = ()

    def __init__(self,
                 *,
                 default=None,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)

    def from_primitive(self, value):
        return pendulum.parse(value)

    def to_primitive(self, value):  # iso8601
        return value.isoformat()

    def to_bytes(self, value):
        return value.isoformat().encode()

    @property
    def type(self):
        return pendulum.DateTime


class UUID(Scalar):

    __slots__ = ()

    def __init__(self,
                 *,
                 default=None,
                 description=Undefined,
                 nullable=True):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)

    def to_primitive(self, value):
        return str(value)

    def from_primitive(self, value):
        return uuid.UUID(value)

    def to_bytes(self, value):
        return value.bytes

    @property
    def type(self):
        return uuid.UUID
