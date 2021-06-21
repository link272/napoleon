from napoleon.web.flask_server import FlaskServer
from napoleon.core.storage.database import Database
from napoleon.core.special.alias import Alias

from pony.orm import db_session
from flask import request


class PersistentFlaskServer(FlaskServer):

    database = Alias(Database)

    def _build_internal(self):
        super()._build_internal() # noqa
        self.database.initialize()

    def build_app(self):
        app = super().build_app()
        return self.build_persistent_layer(app)

    def build_persistent_layer(self, flask_app): # noqa

        def _enter_session():
            session = db_session()
            request.pony_session = session
            session.__enter__()

        def _exit_session(exception):
            session = getattr(request, 'pony_session', None)
            if session is not None:
                session.__exit__(exc=exception)

        flask_app.before_request(_enter_session)
        flask_app.teardown_request(_exit_session)
        return flask_app
