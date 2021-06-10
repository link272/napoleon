from napoleon.core.cmd import CommandLine
from napoleon.core.paths import PATHS

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
    cmd = cmd_class.from_cmd()
    app = Application.from_config("application", cmd.serialize())
    app.cmd = cmd
    return app
