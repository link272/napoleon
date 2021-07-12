from flask import Flask, request
import secrets
from napoleon.properties import PlaceHolder, Boolean, String, AbstractObject, Instance, Integer, List
from napoleon.core.network.http import HTTPQuery
from napoleon.core.network.client import Client
from napoleon.core.application import Application
from napoleon.core.daemon.server import ThreadedServer
from napoleon.tools.singleton import exist
from napoleon.core.special.path import FilePath
from napoleon.core.special.alias import Alias

import threading
from pathlib import Path
from flask_cors import CORS
from flask_cachebuster import CacheBuster


class StaticCache(AbstractObject):

    hash_size = Integer(5)
    extensions = List(String(), default=['.js', '.css'])


class FlaskServer(ThreadedServer):

    secret_key = String(default=secrets.token_urlsafe)
    _shutdown_token = PlaceHolder(default=secrets.token_urlsafe)
    app = PlaceHolder()
    server_client = Alias(Client)
    debug = Boolean(default=True)
    key_filepath = FilePath(lambda: Application().paths.docs / Path("crt.pem"))
    crt_filepath = FilePath(lambda: Application().paths.docs / Path("crt.pem"))
    template_folder = FilePath(lambda: Application().paths["templates"])
    static_folder = FilePath(lambda: Application().paths["static"])
    enable_cors = Boolean(default=False)
    static_cache = Instance(StaticCache)

    def _build_internal(self):
        self.app = self.build_app()

    def get_ssl_context(self):
        context = None
        if self.server_client.scheme == "https":
            if exist(self.key_filepath) and exist(self.crt_filepath):
                context = (self.crt_filepath, self.key_filepath)
            else:
                context = "adhoc"
        return context

    def _start_thread(self):
        self._thread = threading.Thread(target=self.app.run,
                                        kwargs={'host': self.server_client.host,
                                                'port': self.server_client.port,
                                                "debug": self.debug,
                                                "use_reloader": False,
                                                "ssl_context": self.get_ssl_context()},  # noqa
                                        daemon=self.daemon)
        self._thread.start()

    def _stop_thread(self):
        with self.server_client:
            self.server_client.send(HTTPQuery(root=f"/shutdown/{self._shutdown_token}", method="POST"))

    def build_app(self):
        return self.build_base_app()

    def build_base_app(self):
        flask_app = Flask(__name__,
                          template_folder=str(self.template_folder) if exist(self.template_folder) else "",
                          static_folder=str(self.static_folder) if exist(self.static_folder) else "")
        if self.enable_cors:
            CORS(flask_app)

        if exist(self.static_cache):
            config = self.static_cache.serialize()
            cache_buster = CacheBuster(config=config)
            cache_buster.init_app(flask_app)

        flask_app.secret_key = self.secret_key

        self.build_shutdown_mechanism(flask_app)

        return flask_app

    def build_shutdown_mechanism(self, flask_app):

        @flask_app.route('/shutdown/<token>', methods=['POST'])
        def shutdown(token):
            if secrets.compare_digest(self._shutdown_token, token):
                request.environ.get('werkzeug.server.shutdown')()
            return "", 204

    def add_view(self, view, route):
        self.app.add_url_rule(route, view_func=view)
