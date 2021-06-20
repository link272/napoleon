from napoleon.properties import String, Integer, AbstractObject

import logging
import logging.handlers


class Tracer(AbstractObject):

    level: str = String("INFO", enum=["DEBUG", "INFO", "WARNING", "ERROR"])
    formatting: str = String("%(asctime)s :: %(levelname)s :: %(message)s")
    name: str = String("default")

    def _clean_internal(self):
        logger = logging.getLogger(self.name)
        while logger.hasHandlers():
            logger.removeHandler(logger.handlers[0])