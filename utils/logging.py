import logging
import logging.config

from yaml import load
from yaml.loader import SafeLoader


def get_logging_config():
    with open("config/default.yaml", "r") as f:
        config = load(f, Loader=SafeLoader)
    return config


def setup_logging():
    config = get_logging_config()
    root_logger = logging.getLogger("root")
    root_logger.handlers.clear()
    logging.config.dictConfig(config["logging"])
    logging.captureWarnings(True)
    root_logger.setLevel(config["logging_level"])
