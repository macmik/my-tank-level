import logging
from collections import deque
from threading import Lock

from worker import Worker


logger = logging.getLogger(__name__)


class MeasurementConsumer(Worker):
    def __init__(self, config, stop_event, queue):
        super().__init__(config, stop_event, queue)
        self._internal_queue = deque([], maxlen=100000)
        self._queue_lock = Lock()

    def _do(self):
        measurement = self._queue.get()
        logger.info(f'New measurement collected, {measurement}.')
        with self._queue_lock:
            self._internal_queue.append(measurement)

    def get_last_measurement(self):
        with self._queue_lock:
            if self._internal_queue:
                return self._internal_queue[-1]
            return None
