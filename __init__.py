from napoleon.core.cmd import CMD
from napoleon.core.paths import PATHS
from napoleon.core.vault import VAULT
from napoleon.core.utils.machine import PLATFORM

import napoleon.core.daemon.server
import napoleon.core.daemon.scheduler

import napoleon.core.network.client
import napoleon.core.network.interface
import napoleon.core.network.http

import napoleon.core.special.hidden
import napoleon.core.special.path

import napoleon.core.tasks.context
import napoleon.core.tasks.graph_machine

import napoleon.core.utils.encoders
import napoleon.core.utils.retry
import napoleon.core.utils.timer

import napoleon.core.trace

from napoleon.core.application import Application


def configure():
    return Application.from_config("application", CMD.serialize())
