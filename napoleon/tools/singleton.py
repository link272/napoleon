class NothingType(object):
    """
    Used when updating object when None is ambiguous
    """

    _singleton = None

    def __new__(cls):
        if NothingType._singleton is None:
            NothingType._singleton = super(NothingType, cls).__new__(cls)
        return NothingType._singleton

    def __str__(self):
        return "Nothing"

    def __repr__(self):
        return "Nothing"


Nothing = NothingType()


def exist(v):
    return v is not Nothing


class UndefinedType(object):
    """
    Used in class declaration when None is ambiguous
    """

    _singleton = None

    def __new__(cls):
        if UndefinedType._singleton is None:
            UndefinedType._singleton = super(UndefinedType, cls).__new__(cls)
        return UndefinedType._singleton

    def __str__(self):
        return "Undefined"

    def __repr__(self):
        return "Undefined"

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


Undefined = UndefinedType()


def is_define(v):
    return v is not Undefined

