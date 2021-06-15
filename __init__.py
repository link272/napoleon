from napoleon.core.cmd import CommandLine
from napoleon.core.paths import Paths
from napoleon.core.vault import Vault

import napoleon.core.network.client
import napoleon.core.network.interface
import napoleon.core.network.http

import napoleon.core.special.hidden
import napoleon.core.special.path

import napoleon.core.utils.encoders
import napoleon.core.utils.retry
import napoleon.core.utils.timer

import napoleon.core.trace

from napoleon.core.application import Application


def configure(cmd_class=CommandLine):
    cmd = cmd_class.from_cmd(add_help=True)
    paths = Paths.from_config(cmd.paths_config_file, cmd.serialize())
    vault = Vault.from_base64_key(paths.vault.read_text())
    app = Application.from_config(Application.__name__.lower(), cmd.serialize())
    app.cmd = cmd
    app.paths = paths
    app.vault = vault
    return app
