from napoleon.properties import AbstractObject


class CronAction(AbstractObject):

    def execute(self, app):
        raise NotImplementedError
