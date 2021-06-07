from napoleon.core.utils.encoders import Transformer
from napoleon.core.network.interface import Interface
from napoleon.core.network.client import Client
from napoleon.properties import String, Instance, Map, List, AbstractObject, Float, Boolean, PlaceHolder
from napoleon.core.utils.retry import Retrier, retry
from napoleon.tools.singleton import exist, Nothing
import requests


class HTTPClient(Client):

    verify: bool = Boolean()
    scheme = String("https")
    read_timeout = Float(3.)

    def to_url(self):
        return "".join((self.scheme, "://", self.host, ":", str(self.port)))

    def to_auth(self):
        return (self.user, self.password) if self.user != "" and self.password != "" else None


class HTTPQuery(AbstractObject):

    headers: dict = Map(String())
    params: dict = Map(String())
    root = String("/")
    method = String("GET", enum=["GET", "POST", "PUT", "HEAD", "PATCH"])
    encoders: list = List(Instance(Transformer))
    decoders: list = List(Instance(Transformer))
    read_timeout = Float(1.)

    def encode(self, data):
        for encoder in self.encoders:
            data = encoder.transform(data)
        return data

    def decode(self, content):
        for decoder in self.decoders:
            content = decoder.transform(content)
        return content


class HTTPSession(AbstractObject):

    client: HTTPClient = Instance(HTTPClient)
    _session = PlaceHolder()

    def _check_internal(self):
        assert isinstance(self.client, HTTPClient)

    def __enter__(self):
        if self.client.lock:
            if not exist(self._session):
                self._session = requests.Session()

    def refresh(self):
        with self.client.lock:
            self._session.close()
            self.client.check_activity()
            self._session = requests.Session()

    def send(self, query, data=None, files=None, json=None):
        self.client.wait_for_activity()
        url = "".join((self.client.to_url(), query.root))

        response = self._session.request(query.method,
                                         url,
                                         params=query.params,
                                         data=data,
                                         json=json,
                                         headers=query.headers,
                                         auth=self.client.to_auth(),
                                         timeout=(self.client.socket_timeout, query.read_timeout),
                                         verify=self.client.verify,
                                         files=files)
        try:
            response.raise_for_status()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.HTTPError) as e:
            self.refresh()
            raise e

        return response.content

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.client.lock:
            self._session.close()
            self._session = Nothing


class HTTPInterface(Interface):

    queries: dict = Map(Instance(HTTPQuery))
    retrier = Instance(Retrier, default=Retrier)  # noqa
    session = Instance(HTTPSession)

    def _check_internal(self):
        super()._check_internal()  # noqa
        assert isinstance(self.client, HTTPClient)
        assert not exist(self.session) or self.client == self.session.client

    def _build_internal(self):
        if not exist(self.session):
            self.session = HTTPSession(client=self.client)

    def __enter__(self):
        self.session.__enter__()

    @retry
    def send(self, query_name, path="", params={}, data=None, headers={}, files=None):  # noqa
        query = self.queries[query_name].copy()
        query.params.update(params)
        query.headers.update(headers)
        query.root = query.root + path
        data = query.encode(data)
        content = self.session.send(query, data=data, files=files)
        return query.decode(content)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.__exit__(exc_type, exc_val, exc_tb)
