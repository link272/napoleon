from napoleon.core.application import Application
from napoleon.properties import String, Instance, List
from napoleon.core.utils.timer import Timer
from napoleon.tools.context import temporary_state
from napoleon.core.tasks.graph_machine import BaseAction, DEFAULT
from napoleon.tools.collection import empty


class CheckService(BaseAction):

    client_names = List(String())
    timer = Instance(Timer, default=Timer)

    def execute(self, context):
        for name, client in Application().clients.items():
            if empty(self.client_names) or name in self.client_names:
                with temporary_state(client, timer=self.timer):
                    if not client.check_activity():
                        self.log.error(f"Service {name} is down")
        return DEFAULT
