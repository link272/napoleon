from munch import Munch
from napoleon.properties.container import Map


class Bunch(Map):

    _type = Munch
