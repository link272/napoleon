from munch import Munch
from napoleon.tools.singleton import Map


class Bunch(Map):

    _type = Munch
