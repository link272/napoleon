from napoleon.properties import PlaceHolder, Boolean, Float
from napoleon.core.abstract import AbstractDaemon
from napoleon.tools.singleton import Nothing, exist
import time


class ThreadedServer(AbstractDaemon):

    is_enable = Boolean(default=True)
    _thread = PlaceHolder()
    grace_delay: float = Float(2.0)
    daemon: bool = Boolean(default=True)

    def _clean_internal(self):
        self.stop()

    def _start_thread(self):
        raise NotImplementedError

    @property
    def is_active(self):
        return exist(self._thread) and self._thread.is_alive()

    def __del__(self):
        self.shutdown()
        super().__del__()

    def shutdown(self):
        self.stop()

    def _stop_thread(self):
        raise NotImplementedError

    def start(self):
        if self.is_enable and not self.is_active:
            self._start_thread()
            self.log.info("Server is up")

    def stop(self):
        if self.is_active:
            try:
                self._stop_thread()
            except Exception as ex:
                self.log.error(f"Failed to stop the server: {ex}")
            else:
                time.sleep(self.grace_delay)
                if self.is_active:
                    self.log.error(f"Failed to stop the server: Timeout")
                else:
                    self._thread = Nothing
                    self.log.info("Server is down")
