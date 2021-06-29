from napoleon.properties import AbstractObject


class GraphAction(AbstractObject):

    def run(self, context):
        self.execute(self.execute, args=(context,))
