from napoleon.core.utils.encoders import Transformer
from napoleon.core.network.client import Client, Interface
from napoleon.properties import String, Instance, Map, List, AbstractObject, Float, Boolean, PlaceHolder
from napoleon.core.utils.retry import Retrier, retry
from napoleon.tools.singleton import exist, Nothing
import requests


class HTTPClient(Client):

    verify: bool = Boolean()
    scheme = String("https")
    read_timeout = Float(3.)
    _session = PlaceHolder()
    _active_interfaces = PlaceHolder()

    def _build_internal(self):
        super()._build_internal() # noqa
        self._active_interfaces = 0

    def to_url(self):
        return "".join((self.scheme, "://", self.host, ":", str(self.port)))

    def to_auth(self):
        return (self.user, self.password) if self.user != "" and self.password != "" else None

    def __enter__(self):
        with self.lock:
            if not exist(self._session):
                self._session = requests.Session()
                self._session.auth = self.to_auth()
                self._session.verify = self.verify
            self._active_interfaces += 1

    def refresh(self):
        with self.lock:
            self._session.close()
            self.check_activity()
            self._session = requests.Session()
            self._session.auth = self.to_auth()
            self._session.verify = self.verify

    def send(self, query, data=None, files=None, json=None):
        self.wait_for_activity()
        url = "".join((self.to_url(), query.root))

        response = self._session.request(query.method,
                                         url,
                                         params=query.params,
                                         data=data,
                                         json=json,
                                         headers=query.headers,
                                         timeout=(self.socket_timeout, query.read_timeout),
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
        with self.lock:
            self._active_interfaces -= 1
            if self._active_interfaces == 0:
                self._session.close()
                self._session = Nothing


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


class HTTPInterface(Interface):

    queries: dict = Map(Instance(HTTPQuery))
    retrier = Instance(Retrier, default=Retrier)  # noqa

    def _check_internal(self):
        super()._check_internal()  # noqa
        assert isinstance(self.client, HTTPClient)

    def __enter__(self):
        self.client.__enter__()

    @retry
    def send(self, query_name, path="", params={}, data=None, headers={}, files=None):  # noqa
        query = self.queries[query_name].copy()
        query.params.update(params)
        query.headers.update(headers)
        query.root = query.root + path
        data = query.encode(data)
        content = self.client.send(query, data=data, files=files)
        return query.decode(content)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)
