from napoleon.properties import String, Boolean, PlaceHolder, AbstractObject, Alias, Float
from napoleon.core.paths import PATHS, FilePath, Path
from pony.orm import Database as PonyDatabase
from napoleon.core.network.client import Client, CLIENTS

DATABASES = {}


class Database(AbstractObject):

    name = String("artemis")
    _engine = PlaceHolder()
    _is_initialised = PlaceHolder()

    def _build_internal(self):
        DATABASES[self.name] = self
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

    filepath = FilePath(PATHS.data / Path("db.db3"))
    create_db = Boolean(default=True)
    timeout = Float(default=0.5)

    def bind(self):
        self._engine.bind("sqlite",
                          filename=str(self.filepath),
                          create_db=self.create_db,
                          timeout=self.timeout)


class PostgresDatabase(Database):

    client: Client = Alias(Client, CLIENTS)
    database_name = String("artemis")

    def bind(self):
        self._engine.bind(provider='postgres',
                          user=self.client.user,
                          password=self.client.password,
                          host=self.client.host,
                          dbname=self.database_name,
                          port=self.client.port)

class MysqlDatabase(Database):

    client: Client = Alias(Client, CLIENTS)
    database_name = String("artemis")

    def bind(self):
        self._engine.bind(provider='mysql',
                          host=self.client.host,
                          user=self.client.user,
                          passwd=self.client.password,
                          db=self.database_name,
                          port=self.client.port,
                          connect_timeout=self.client.socket_timeout)

