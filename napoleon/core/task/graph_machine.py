import importlib
from collections import deque

import pendulum

from napoleon.core.shared.config import Configurable
from napoleon.properties import String, AbstractObject, PlaceHolder, List, Instance, Boolean, JSON
from napoleon.tools.singleton import is_define, Undefined

DEFAULT = "DEFAULT"
EXIT = "EXIT"


class Action(AbstractObject):

    config = JSON(default=dict)
    executable: str = String()
    force_reload = Boolean()
    name = String()
    is_enable = Boolean(default=True)
    allow_failure = Boolean()

    def __call__(self, context):
        return self.run(context)

    def run(self, context):
        code = DEFAULT
        if self.is_enable:
            start_time = pendulum.now()
            code = self.execute(context) or DEFAULT
            end_time = pendulum.now()
            self.log.info(f"Action: {self.name}, elapsed time: {(end_time - start_time).total_seconds()}s")
        else:
            self.log.info(f"Action: {self.name} is disable")
        return code

    def __str__(self):
        return self.name

    def execute(self, context):
        action = self.build_dynamic_action()
        return action.execute(context)

    def build_dynamic_action(self):
        path = self.executable.split(".")
        module_name = ".".join(path[:-1])
        action_class_name = path[-1]
        module = importlib.import_module(module_name)
        if self.force_reload:
            importlib.reload(module)
        action_class = getattr(module, action_class_name)
        return action_class.deserialize(self.config)


class Transition(AbstractObject):

    tag = String(DEFAULT)
    previous = String()
    next = String()


class GraphMachine(Configurable):

    """
    Apply actions on given context, allowing to organize a large application
    """

    actions: list = List(Instance(Action), merge_on="name")
    transitions: list = List(Instance(Transition))
    graph: dict = PlaceHolder(default=dict)
    name = String("GraphMachine")

    def _build_internal(self):
        _map = dict()
        for action in self.actions:
            _map[action.name] = action
            self.graph[action] = dict()

        for link in self.transitions:
            self.graph[_map[link.previous]][link.tag] = _map[link.next]

    def execute(self, context):
        self.log.info(f"Graph machine is running with the following tags: {', '.join(context.tags)}")

        first = self.actions[0]

        if context.resume_action:
            for action in self.actions:
                if action.name == context.resume_action:
                    first = action

        queue = deque([first])

        code = DEFAULT

        while queue:
            node = queue.pop()
            try:
                code = node.run(context)
            except Exception as e:
                self.log.exception(f"An exception occurs: {e}, action: {node.name}, allow_failure: {node.allow_failure}")
                if not node.allow_failure:
                    code = EXIT
                    context.resume_action = node.name
                    context.error_msg = str(e)

            context.save()

            if code == EXIT:
                break
            else:
                context.tags.add(code)

            child = Undefined
            for tag, sub_node in self.graph[node].items():
                if tag in context.tags and tag != DEFAULT:
                    child = sub_node
                elif tag == DEFAULT and not is_define(child):
                    child = sub_node
                else:
                    pass
            if is_define(child):
                queue.appendleft(child)
            else:
                self.log.info(f"No successor found for action: {node.name}")

        return context
