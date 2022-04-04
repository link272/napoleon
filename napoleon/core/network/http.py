import threading

import requests

from napoleon.core.decorator.retry import retry
from napoleon.core.network.base import BaseClient, BaseInterface, BaseAuthentication
from napoleon.core.network.netloc import NetworkLocalization
from napoleon.core.vault.property import Secret
from napoleon.properties import String, Instance, Map, AbstractObject, Float, Boolean, PlaceHolder
from napoleon.tools.pipeline import Pipeline
from napoleon.tools.singleton import Nothing


class BasicAuthentication(BaseAuthentication):

    user = String()
    password = Secret()


class HTTPClient(BaseClient):

    verify: bool = Boolean()
    scheme = String("https")
    read_timeout = Float(3.)
    auth = Instance(BaseAuthentication)
    netloc = Instance(NetworkLocalization)
    _session = PlaceHolder()
    _active_interfaces = PlaceHolder(default=0)
    _active_flag = PlaceHolder(default=threading.Event)
    _lock = PlaceHolder(default=threading.RLock)

    def _build_internal(self):
        self._active_flag.clear()
        self._active_interfaces = 0

    def to_url(self):
        return "".join((self.scheme, "://", self.netloc.host, ":", str(self.netloc.port)))

    def to_auth(self):
        return (self.auth.user, self.auth.password) if isinstance(self.auth, BasicAuthentication) else None

    def __enter__(self):
        with self._lock:
            if self._session is None:
                self._session = requests.Session()
                self._session.auth = self.to_auth()
                self._session.verify = self.verify
            self._active_interfaces += 1

    def refresh(self):
        with self._lock:
            self._session.close()
            self.netloc.check_remote()
            self._session = requests.Session()
            self._session.auth = self.to_auth()
            self._session.verify = self.verify

    def send(self, query, data=None, files=None, json=None):
        url = "".join((self.to_url(), query.root))

        response = self._session.request(query.method,
                                         url,
                                         params=query.params,
                                         data=data,
                                         json=json,
                                         headers=query.headers,
                                         timeout=(self.netloc.socket_timeout, query.read_timeout),
                                         files=files)
        try:
            response.raise_for_status()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.HTTPError) as e:
            self.refresh()
            raise e

        return response

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            self._active_interfaces -= 1
            if self._active_interfaces == 0:
                self._session.close()
                self._session = Nothing


class HTTPQuery(AbstractObject):

    headers: dict = Map(String())
    params: dict = Map(String())
    root = String("/")
    method = String("GET", enum=["GET", "POST", "PUT", "HEAD", "PATCH"])
    read_timeout = Float(1.)


class HTTPInterface(BaseInterface):

    queries: dict = Map(Instance(HTTPQuery))

    def _check_internal(self):
        super()._check_internal()  # noqa
        assert isinstance(self.client, HTTPClient)

    def __enter__(self):
        self.client.__enter__()

    @retry()
    def send(self, query_name, path="", params={}, data=None, headers={}, files=None):  # noqa
        query = self.queries[query_name].copy()
        query.params.update(params)
        query.headers.update(headers)
        query.root = query.root + path
        return Pipeline(self.client.send(query, data=data, files=files).content)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.__exit__(exc_type, exc_val, exc_tb)
