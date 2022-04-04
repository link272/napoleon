import importlib

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_PAUSED, STATE_RUNNING
from apscheduler.triggers.cron import CronTrigger

from napoleon.core.daemon.base import BaseDaemon
from napoleon.core.shared.application import Application
from napoleon.properties import Boolean, String, Integer, PlaceHolder, Map, MutableSingleton, Instance, AbstractObject, \
    iter_properties, JSON

CRON_REGEX = r"/(\d+,)+\d+|(\d+(\/|-)\d+)|\d+|\*/"


class Trigger(AbstractObject):
    """Explicit crontab"""

    year = String(pattern=CRON_REGEX)
    month = String(pattern=CRON_REGEX)
    day = String(pattern=CRON_REGEX)
    day_of_week = String(enum=["mon", "tue", "wed", "thu", "fri", "sat", "sun"])
    hour = String(pattern=CRON_REGEX)
    minute = String(pattern=CRON_REGEX)
    second = String(pattern=CRON_REGEX)
    jitter = Integer(1)

    def _clean_internal(self):
        for key, field in iter_properties(self.__class__):
            self.__setattr__(key, field.default)


class CronJob(AbstractObject):
    """A CronJob execute a dynamic python module"""

    trigger = Instance(Trigger)
    coalesce = Boolean(default=True)
    misfire_grace_time = Integer(5)
    max_instances = Integer(1)
    is_enable = Boolean(default=True)
    message = String()
    config = JSON(default=dict)
    executable: str = String()
    name = String()
    _action = PlaceHolder()

    def __str__(self):
        return self.name

    def execute(self, app):
        try:
            if self.message:
                self.log.info(self.message)
            if self.is_enable:
                self._action.execute(app)
        except Exception as ex:
            self.log.error(ex)

    def _build_internal(self):
        path = self.executable.split(".")
        module_name = ".".join(path[:-1])
        action_class_name = path[-1]
        module = importlib.import_module(module_name)
        importlib.reload(module)
        action_class = getattr(module, action_class_name)
        self._action = action_class.deserialize(self.config)


class Scheduler(BaseDaemon, metaclass=MutableSingleton):
    """Backend around APScheduler"""

    cron_jobs: dict = Map(Instance(CronJob))
    is_enable = Boolean(default=True)
    backend: BackgroundScheduler = PlaceHolder(default=BackgroundScheduler)

    def is_running(self):
        return self.backend.state == STATE_RUNNING

    def is_paused(self):
        return self.backend.state == STATE_PAUSED

    def _build_internal(self):
        for name, cron in self.cron_jobs.items():
            trigger = CronTrigger(**{k: v for k, v in cron.trigger.serialize().items()
                                     if v and k != "class_name"})
            self.backend.add_job(cron.execute,
                                 args=(Application(),),
                                 trigger=trigger,
                                 id=name,
                                 name=name,
                                 misfire_grace_time=cron.misfire_grace_time or None,
                                 coalesce=cron.coalesce,
                                 max_instances=cron.max_instances,
                                 replace_existing=True)

    def _clean_internal(self):
        self.stop()
        for job in self.backend.get_jobs():
            job.remove()

    def start(self):
        if self.is_enable and not self.is_active:
            if self.backend.state == STATE_PAUSED:
                self.backend.resume()
            else:
                self.backend.start()
                self.log.info("Scheduler is up")

    @property
    def is_active(self):
        return self.backend.running

    def __del__(self):
        self.shutdown()
        super().__del__()

    def shutdown(self):
        if self.is_active:
            self.backend.shutdown()
            self.log.info("Scheduler is down")

    def stop(self):
        if self.backend.state == STATE_RUNNING:
            self.backend.pause()
