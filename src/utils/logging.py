import logging
import logging.config

from src.utils.access_config import config_manager


def setup_logging():
    config = config_manager.get_property("logging")
    logging_level = config_manager.get_property("logging_level") or "INFO"
    root_logger = logging.getLogger("root")
    root_logger.handlers.clear()
    logging.config.dictConfig(config)
    logging.captureWarnings(True)
    root_logger.setLevel(logging_level)
