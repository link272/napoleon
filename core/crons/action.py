from napoleon.properties import AbstractObject


class CronAction(AbstractObject):

    def run(self, app):
        raise NotImplementedError
