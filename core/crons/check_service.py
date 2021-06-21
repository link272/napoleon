from napoleon.properties import String, Instance, List
from napoleon.core.utils.timer import Timer
from napoleon.tools.context import temporary_state
from napoleon.tools.collection import empty
from napoleon.core.crons.base import CronAction


class CheckService(CronAction):

    client_names = List(String())
    timer = Instance(Timer, default=Timer)

    def run(self, app):
        for name, client in app.clients.items():
            if empty(self.client_names) or name in self.client_names:
                with temporary_state(client, timer=self.timer):
                    if not client.check_activity():
                        self.log.error(f"Service {name} is down")