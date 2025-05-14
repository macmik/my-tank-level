import time
import logging
from worker import Worker
from datetime import datetime as DT
from datetime import timedelta as TD
from measurement import Measurement

import serial


logger = logging.getLogger(__name__)


class MeasurementReader(Worker):
    def __init__(self, config, stop_event, queue):
        super().__init__(config, stop_event, queue)
        logger.info('Initializing serial.')
        self._connection = serial.Serial('/dev/serial0', baudrate=9600, timeout=1)  # Open port with baud rate
        self._last_measurement_added = DT.now()
        self._interval_sec = TD(seconds=config['store_interval_sec'])
        logger.info('Initialize serial done.')

    def _do(self):
        if self._connection.in_waiting > 0:
            data = self._connection.read(4)
            logger.debug(f'New raw data collected {str(data)}.')
            if not self._validate(data):
                logger.debug('Validation failed.')
                time.sleep(0.1)
                return
            logger.debug('Validation passed.')
            distance = (data[1] << 8) + data[2]
            ts = DT.now()
            if ts - self._last_measurement_added > self._interval_sec:
                logger.info(f'Put new measurement to queue, {str(ts)}, {str(distance)} mm.')
                self._queue.put(Measurement(ts, distance))
                self._last_measurement_added = ts

        time.sleep(0.1)

    def _validate(self, data):
        if not data[0] == 0xFF:
            return False
        if not sum(data[:3]) & 0x00FF == data[3]:
            return False
        return True
