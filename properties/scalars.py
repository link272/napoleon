import pendulum
import uuid
from .base import Property
from ..tools.singleton import Undefined, Intrinsic, Nothing
from ..tools.bson import to_bson, from_bson
import json
import base64

class Scalar(Property):  # noqa

    __slots__ = ()

    def from_primitive(self, value):  # noqa
        return value

    def to_primitive(self, value):  # noqa
        return value

    def from_string(self, value):
        raise NotImplementedError

    def to_string(self, value):
        raise NotImplementedError

    def to_bytes(self, value):
        raise NotImplementedError


class Boolean(Scalar):

    __slots__ = ()
    _type = bool

    def system_default(self):
        return False

    def from_string(self, value):
        return bool(value)

    def to_string(self, value):
        return str(value)

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(self.to_string(value).encode())


class Float(Scalar):

    __slots__ = ("minimum", "maximum", "exclusive_minimum", "exclusive_maximum", "multiple_of",)
    _type = float

    def __init__(self,
                 default=Intrinsic,
                 minimum=Undefined,
                 maximum=Undefined,
                 exclusive_minimum=Undefined,
                 exclusive_maximum=Undefined,
                 multiple_of=Undefined,
                 description=Undefined,
                 nullable=False):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.minimum = minimum
        self.maximum = maximum
        self.exclusive_minimum = exclusive_minimum
        self.exclusive_maximum = exclusive_maximum
        self.multiple_of = multiple_of

    def system_default(self):
        return 0.0

    def from_string(self, value):
        return float(value)

    def to_string(self, value):
        return str(value)

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(self.to_string(value).encode())


class Integer(Float):

    __slots__ = ()
    _type = int

    def system_default(self):
        return 0

    def from_string(self, value):
        return int(value)

    def to_string(self, value):
        return str(value)

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(self.to_string(value).encode())

class Symbol(Scalar):  # noqa

    __slots__ = ("pattern", "format")
    _type = str

    def __init__(self,
                 default=Intrinsic,
                 pattern=Undefined,
                 format=Undefined,  # noqa
                 description=Undefined,
                 nullable=False):
        super().__init__(default=default,
                         description=description,
                         nullable=nullable)
        self.pattern = pattern
        self.format = format

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(self.to_string(value).encode())


class String(Symbol):

    __slots__ = ("min_length", "max_length", "enum")
    _type = str

    def __init__(self,
                 default=Intrinsic,
                 enum=Undefined,
                 min_length=Undefined,
                 max_length=Undefined,
                 pattern=Undefined,
                 format=Undefined,  # noqa
                 description=Undefined,
                 nullable=False
                 ):
        super().__init__(default=default,
                         description=description,
                         pattern=pattern,
                         format=format,
                         nullable=nullable)
        self.min_length = min_length
        self.max_length = max_length
        self.enum = enum

    def system_default(self):
        return ""

    @classmethod
    def as_constant(cls, default):
        return cls(default=default, enum=[default])

    def to_string(self, value):
        return str(value)

    def from_string(self, value):
        return str(value)

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(self.to_string(value).encode())


class Bytes(Scalar):

    __slots__ = ()
    _type = bytes

    def system_default(self):
        return b""

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(value)

    def from_bytes(self, value):
        return base64.urlsafe_b64decode(value)

    def to_string(self, value):
        return self.to_bytes(value).decode()

    def from_string(self, value):
        return self.from_bytes(value.encode())


class Blob(Scalar):

    __slots__ = ()

    def system_default(self):
        return Nothing


class JSON(Scalar):

    __slots__ = ()
    _type = dict

    def system_default(self):
        return self._type()

    def to_bytes(self, value):
        return to_bson(value)

    def from_bytes(self, value):
        return from_bson(value)

    def from_string(self, value):
        return json.loads(value)

    def to_string(self, value):
        return json.dumps(value)


class DateTime(Symbol):

    __slots__ = ()
    _type = pendulum.DateTime

    def __init__(self,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):
        super().__init__(
            default=default,
            description=description,
            format="date-time",
            nullable=nullable
        )

    def from_string(self, value):
        return pendulum.parse(value)

    def system_default(self):
        return Nothing

    def to_string(self, value):  # iso8601
        return value.isoformat()

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(self.to_string(value).encode())


class UUID(Symbol):

    __slots__ = ()
    _type = uuid.UUID

    def __init__(self,
                 default=Intrinsic,
                 description=Undefined,
                 nullable=False):
        super().__init__(
            default=default,
            description=description,
            pattern="[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            nullable=nullable
        )

    def system_default(self):
        return Nothing

    def to_string(self, value):
        return str(value)

    def from_string(self, value):
        return uuid.UUID(value)

    def to_bytes(self, value):
        return base64.urlsafe_b64encode(value.bytes)

    def from_bytes(self, value):
        return uuid.UUID(bytes=base64.urlsafe_b64decode(value))
