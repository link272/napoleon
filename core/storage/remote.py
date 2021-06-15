from napoleon.properties import String, Alias
from napoleon.core.storage.database import Database
from napoleon.core.network.client import Client
from napoleon.core.application import Application


class PostgresDatabase(Database):

    client: Client = Alias(Client, lambda: Application().clients)
    database_name = String("artemis")

    def bind(self):
        self._engine.bind(provider='postgres',
                          user=self.client.user,
                          password=self.client.password,
                          host=self.client.host,
                          dbname=self.database_name,
                          port=self.client.port)


class MysqlDatabase(Database):

    client: Client = Alias(Client, lambda: Application().clients)
    database_name = String("artemis")

    def bind(self):
        self._engine.bind(provider='mysql',
                          host=self.client.host,
                          user=self.client.user,
                          passwd=self.client.password,
                          db=self.database_name,
                          port=self.client.port,
                          connect_timeout=self.client.socket_timeout)