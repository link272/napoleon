from napoleon.core.network.interface import Interface
from napoleon.core.network.client import Client
from napoleon.properties import Instance, PlaceHolder, DateTime, Set, Integer, Boolean, String, Map, AbstractObject, List
from napoleon.tools.singleton import Nothing, exist
from napoleon.core.utils.encoders import Transformer
from napoleon.core.utils.retry import Retrier, retry


from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


class CassandraClient(Client):

    _cluster = PlaceHolder()
    compression = Boolean(default=True)
    protocol_version = Integer(4)
    metrics_enabled = Boolean()
    schema_metadata_enabled = Boolean(default=True)
    token_metadata_enabled = Boolean(default=True)
    contact_points = Set(String())
    executor_threads = Integer(2)
    host = String()

    def _check_internal(self):
        assert bool(self.contact_points) != bool(self.host)

    @property
    def cluster(self):
        if not exist(self._cluster):
            contacts_points = self.contact_points if self.contact_points else (self.host,)
            connect_timeout = int(self.socket_timeout)
            auth = PlainTextAuthProvider(username=self.user, password=self.password)
            self._cluster = Cluster(contacts_points=contacts_points,
                                    port=self.port,
                                    auth_provider=auth,
                                    compression=self.compression,
                                    protocol_version=self.protocol_version,
                                    metrics_enabled=self.metrics_enabled,
                                    connect_timeout=connect_timeout,
                                    schema_metadata_enabled=self.schema_metadata_enabled,
                                    token_metadata_enabled=self.token_metadata_enabled,
                                    executor_threads=self.executor_threads
                                    )
        return self._cluster

    def _clean_internal(self):
        if exist(self._cluster):
            self._cluster.shutdown()
            self._cluster = Nothing


class CassandraQuery(AbstractObject):

    encoders: list = List(Interface(Transformer))
    decoders: list = List(Interface(Transformer))

    def encode(self, data):
        for encoder in self.encoders:
            data = encoder.transform(data)
        return data

    def decode(self, content):
        for decoder in self.decoders:
            content = decoder.transform(content)
        return content


class CassandraInterface(Interface):

    queries = Map(Instance(CassandraQuery))
    retrier = Object(Retrier, Retrier())  # noqa
    keyspace = String()
    _session = PlaceHolder()

    def _check_internal(self):
        assert isinstance(self.client, CassandraClient)

    def __enter__(self):
        self._session = self.client.cluster.connect(keyspace=self.keyspace)

    def refresh_session(self):
        with self.client.lock:
            self._session.shutdown()
            self.client.check_activity()
            self._session = self.client.cluster.connect(keyspace=self.keyspace)

    @retry
    def send(self, query_name, data):
        self.wait_for_activity()
        try:
            query = self.queries.get(query_name).build(data)
            response = self._session.execute(query)
        except Exception as e:
            self.handle_error()
        return response

    def handle_error(self):
        self.refresh_session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.shutdown()
        self._session = Nothing