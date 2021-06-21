from napoleon.properties import Boolean, String, Integer, PlaceHolder, Map, MutableSingleton, Instance, AbstractObject,\
    iter_properties
from napoleon.core.cron.action import CronAction
from napoleon.core.daemon.daemon import Daemon
from napoleon.tools.singleton import Nothing
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.base import STATE_PAUSED, STATE_RUNNING
from napoleon.core.application import app


CRON_REGEX = r"/(\d+,)+\d+|(\d+(\/|-)\d+)|\d+|\*/"


class Trigger(AbstractObject):

    year = String(pattern=CRON_REGEX)
    month = String(pattern=CRON_REGEX)
    day = String(pattern=CRON_REGEX)
    day_of_week = String(enum=["mon", "tue", "wed", "thu", "fri", "sat", "sun"])
    hour = String(pattern=CRON_REGEX)
    minute = String(pattern=CRON_REGEX)
    second = String(pattern=CRON_REGEX)
    jitter = Integer(1)

    def to_aps(self):
        aps_cron = {k: v for k, v in self.serialize().items() if v and k != "class_name"}
        return CronTrigger(**aps_cron)

    def _clean_internal(self):
        for key, field in iter_properties(self.__class__):
            self.__setattr__(key, field.system_default())


class CronJob(AbstractObject):

    trigger = Instance(Trigger)
    action: CronAction = Instance(CronAction)
    coalesce = Boolean(default=True)
    misfire_grace_time = Integer(5)
    max_instances = Integer(1)
    is_enable = Boolean(default=True)
    message = String()

    def execute(self, app):
        try:
            if self.message:
                self.log.info(self.message)
            self.action.execute(app)
        except Exception as ex:
            self.log.error(ex)


class Scheduler(Daemon, metaclass=MutableSingleton):

    cron_jobs: dict = Map(Instance(CronJob))
    is_enable = Boolean(default=True)
    backend: BackgroundScheduler = PlaceHolder(default=BackgroundScheduler)

    def is_running(self):
        return self.backend.state == STATE_RUNNING

    def is_paused(self):
        return self.backend.state == STATE_PAUSED

    def _build_internal(self):
        for name, cron in filter(lambda t: t[1].is_enable, self.cron_jobs.items()):
            self.backend.add_job(cron.execute,
                                 args=(app,),
                                 trigger=cron.trigger.to_aps(),
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
