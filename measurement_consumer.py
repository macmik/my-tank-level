import logging
from collections import deque

from worker import Worker


logger = logging.getLogger(__name__)


class MeasurementConsumer(Worker):
    def __init__(self, config, stop_event, queue):
        super().__init__(config, stop_event, queue)
        self._internal_queue = deque([], maxlen=100000)

    def _do(self):
        measurement = self._queue.get()
        logger.info(f'New measurement collected, {measurement}.')
        self._internal_queue.append(measurement)
