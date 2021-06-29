from napoleon.properties import String, AbstractObject, PlaceHolder, List, Instance, Boolean, JSON
from napoleon.core.utils.config import Configurable
from napoleon.tools.singleton import is_define, Undefined
from collections import deque
import pendulum
import importlib
import networkx as nx

DEFAULT = "DEFAULT"
EXIT = "EXIT"


class DynamicAction(AbstractObject):

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
        return action_class.from_json(self.config)


class LinkAction(AbstractObject):

    tag = String(DEFAULT)
    previous = String()
    next = String()


class GraphMachine(Configurable):

    actions: list = List(Instance(DynamicAction), merge_on="name")
    links: list = List(Instance(LinkAction))
    graph = PlaceHolder()
    name = String("GraphMachine")

    def _build_internal(self):
        self.graph = nx.DiGraph()

        _map = dict()
        for action in self.actions:
            _map[action.name] = action
            self.graph.add_node(action, label=str(action))

        for link in self.links:
            self.graph.add_edge(_map[link.previous], _map[link.next], label=link.tag)

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
                self.log.error(f"An exception occurs: {e}, action: {node.name}, allow_failure: {node.allow_failure}")
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
            for sub_node in self.graph.successors(node):
                tag = self.graph[node][sub_node]["label"]
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
