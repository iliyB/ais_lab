import logging
from logging import Logger


def get_logger(logger: Logger) -> Logger:
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
