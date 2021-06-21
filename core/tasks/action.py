from napoleon.properties import AbstractObject


class GraphAction(AbstractObject):

    def run(self, context):
        self.executor.execute(self.execute, args=(context,))
