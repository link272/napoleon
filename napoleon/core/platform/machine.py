import platform as plt
import subprocess

import psutil

from napoleon.core.platform.base import BaseMachine
from napoleon.core.shared.application import Application
from napoleon.properties import AbstractObject, String, Integer, Float, Instance


class CPU(AbstractObject):

    count = Integer(psutil.cpu_count())
    logical = Integer(psutil.cpu_count(logical=True))
    min_freq = Float(psutil.cpu_freq().min)
    max_freq = Float(psutil.cpu_freq().max)

    def usage(self): # noqa
        return psutil.cpu_percent(interval=1., percpu=False)


class RAM(AbstractObject):

    total = Integer(int(psutil.virtual_memory().total))
    available = Integer(int(psutil.virtual_memory().available))

    def usage(self): # noqa
        return psutil.virtual_memory().percent


class Machine(BaseMachine):

    system = String()
    node = String()
    release = String()
    python_version = String(plt.python_version)
    machine = String()
    processor = String()
    git_commit_ref = String()
    cpu = Instance(CPU, default=CPU)
    ram = Instance(RAM, default=RAM)

    @classmethod
    def from_platform(cls):
        return cls.deserialize(plt.uname()._asdict()) # noqa

    def _build_internal(self):
        self.git_commit_ref = self.git_commit_id()

    def git_commit_id(self):
        sha1_ref = ""
        try:
            res = subprocess.run(["git", "-C", Application().paths.root, "show-ref", "--head", "HEAD"], capture_output=True)
            if res.returncode == 0:
                sha1_ref = res.stdout.decode().split("\n")[0].split(" ")[0]
        except Exception as ex:
            self.log.error(f"Unable to get the git commit ID: {ex}")
        return sha1_ref
