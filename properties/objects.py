from .metaclass import SlottedType
import copy
from .scalars import String
from .base import iter_properties
from ..tools.log import LOGGERS, PrintLogger
from ..encoders.json_encoder import JSONEncoder
from ..encoders.hash_encoder import HashEncoder
from ..decoders.json_decoder import JSONDecoder

PRINT_LOGGER = PrintLogger()


class AbstractObject(object, metaclass=SlottedType):

    class_name = String()

    def __init__(self, **kwargs):
        for key, _property in iter_properties(self.__class__): # noqa
            if key in kwargs:
                self.__setattr__(key, kwargs[key])
            else:
                self.__setattr__(key, _property.initialize_default())
        self.class_name = self.__class__.__name__
        self._check_internal()
        self._build_internal()

    def update(self, **kwargs):
        self._clean_internal()
        for key, field in iter_properties(self.__class__): # noqa
            if key in kwargs:
                self.__setattr__(key, kwargs[key])
        self._check_internal()
        self._build_internal()
        return self

    def _clean_internal(self):
        pass

    def _check_internal(self):
        pass

    def _build_internal(self):
        pass

    @property
    def hash(self):
        return HashEncoder().encode(self)

    @property
    def log(self):
        return LOGGERS.get(getattr(self, "logger_name", "default"), PRINT_LOGGER)

    def __del__(self):
        self._clean_internal()

    def copy(self):
        return copy.deepcopy(self)

    def serialize(self):
        return JSONEncoder().encode(self)

    @classmethod
    def deserialize(cls, instance):
        return JSONDecoder().decode(instance, cls)
