import logging
from logging import Logger


def get_logger(name: str, level: str = "INFO") -> Logger:
    """
    Create a namespaced logger with sane defaults.

    Args:
        name (str): Logger name.
        level (str): Logging level (default = "INFO").

    Returns:
        Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(fmt)
        logger.addHandler(handler)

    logger.setLevel(level.upper())  # ensure string levels ("info") still work
    return logger
