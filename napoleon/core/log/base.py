import logging
import logging.handlers

from napoleon.properties import String, AbstractObject


class BaseLogger(AbstractObject):
    """Logging using napoleon ecosystem"""

    level: str = String("INFO", enum=["DEBUG", "INFO", "WARNING", "ERROR"])
    formatting: str = String("%(asctime)s :: %(levelname)s :: %(message)s")
    name: str = String("default")

    def _build_internal(self):
        raise NotImplementedError

    def _clean_internal(self):
        logger = logging.getLogger(self.name)
        while logger.hasHandlers():
            try:
                logger.removeHandler(logger.handlers[0])
            except IndexError as e:
                pass
