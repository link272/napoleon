from napoleon.properties import AbstractObject, String


class SimpleAction1(AbstractObject):

    test = String()

    def execute(self, context):
        context.error_msg = self.test


class SimpleAction2(AbstractObject):

    test = String()

    def execute(self, context):
        context.error_msg = self.test
