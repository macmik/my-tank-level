import sys
import json
import logging
from os import environ
from pathlib import Path
from threading import Event
from queue import Queue

from measurement_reader import MeasurementReader
from measurement_consumer import MeasurementConsumer


from flask import Flask, jsonify


def setup_logging():
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    log_level = environ.get("LOG_LVL", "info")
    if log_level == "dump":
        level = logging.DEBUG
    elif log_level == "info":
        level = logging.INFO
    elif log_level == "error":
        level = logging.ERROR
    elif log_level == "warning":
        level = logging.WARNING
    else:
        logging.error('"%s" is not correct log level', log_level)
        sys.exit(1)
    if getattr(setup_logging, "_already_set_up", False):
        logging.warning("Logging already set up")
    else:
        logging.basicConfig(format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", level=level)
        setup_logging._already_set_up = True


def create_app():
    app = Flask(__name__, static_folder='templates')
    config = json.loads(Path('config.json').read_text())
    setup_logging()

    queue = Queue()
    stop_event = Event()

    measurement_reader = MeasurementReader(config, stop_event, queue)
    measurement_consumer = MeasurementConsumer(config, stop_event, queue)

    measurement_reader.start()
    measurement_consumer.start()

    app.consumer = measurement_consumer
    app.app_config = config

    return app


app = create_app()


@app.route('/state', methods=['GET'])
def state():
    measurement = app.consumer.get_last_measurement()

    response_dict = {
        'timestamp': None,
        'distance_mm': None,
        'level_percent': None
    }

    if measurement:
        response_dict['timestamp'] = measurement.ts.strftime('%Y%m%d-%H:%M:%S')
        response_dict['distance_mm'] = measurement.distance
        response_dict['level_percent'] = round((measurement.distance / app.app_config['tank_height_mm']) * 100.0)

    return jsonify(response_dict)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
