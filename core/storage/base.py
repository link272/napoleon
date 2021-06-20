from napoleon.properties import String, Boolean, PlaceHolder, AbstractObject, Alias, Float
from napoleon.core.paths import FilePath, Path, Paths
from pony.orm import Database as PonyDatabase


class Database(AbstractObject):

    name = String("artemis")
    _engine = PlaceHolder()
    _is_initialised = PlaceHolder()

    def _build_internal(self):
        self._engine = PonyDatabase()
        self._is_initialised = False

    def initialize(self):
        if not self._is_initialised:
            self.bind()
            self._engine.generate_mapping(create_tables=True)
            self._is_initialised = True

    def bind(self):
        raise NotImplementedError

    @property
    def entity(self):
        return self._engine.Entity

    @property
    def db(self):
        return self._engine


class SqliteDatabase(Database):

    filepath = FilePath(lambda: Paths().data / Path("db.db3"))
    create_db = Boolean(default=True)
    timeout = Float(default=0.5)

    def bind(self):
        self._engine.bind("sqlite",
                          filename=str(self.filepath),
                          create_db=self.create_db,
                          timeout=self.timeout)

