from napoleon.core.crons.base import CronAction
from napoleon.properties import String, Instance, List


class Monitoring(CronAction):

    logger_name = String(default="default")

    def execute(self, app):
        self.log.info(f"|cpu|{app.platform.cpu.usage()}|ram|{app.platform.ram.usage()}")
