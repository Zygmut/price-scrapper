import logging
import logging.config
import logging_loki  # type: ignore
from queue import Queue
import sys

# Define the logging configuration dictionary
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simpleFormatter": {
            "format": "[ %(levelname)s ] %(asctime)s - %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "lokiHandler": {
            "queue": Queue(-1),
            "class": "logging_loki.LokiQueueHandler",
            "level": "INFO",
            "formatter": "simpleFormatter",
            "url": "http://localhost:3100/loki/api/v1/push",
            "version": "1",
        },
        "consoleHandler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simpleFormatter",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "price_scrapper": {
            "level": "DEBUG",
            "handlers": ["lokiHandler", "consoleHandler"],
            "propagate": False,
        }
    },
}

# Apply the logging configuration
logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    if name not in LOGGING_CONFIG.get("loggers", {}).keys():  # type: ignore
        print("Logger could not be initialized", file=sys.stderr)
        exit(1)

    return logging.getLogger(name)
