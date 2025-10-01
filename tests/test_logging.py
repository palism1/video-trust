# pytest tests for get_logger
import logging

from src.common.logging_utils import get_logger

FMT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

def test_info_log_emitted(caplog):
    """INFO logs should be caputred and use the expected formatter."""
    logger = get_logger("vt.test.infor", "INFO")

    # capture only this logger's records at INFO+
    with caplog.at_level(logging.INFO, logger="vt.test.info"):
        logger.info("hello world")

    # message made it through
    assert any("hello world" in r.message for r in caplog.records)

    # formatter is set to our format
    handler = logger.handlers[0]
    assert isinstance(handler.formatter, logging.Formatter)
    assert handler.formatter._fmt == FMT # ok to peek in tests

def test_lowercase_level_normalized(caplog):
    """String levels like 'debug' should work (normalized to DEBUG)."""
    logger = get_logger("vt.test.debug", "debug")
    with caplog.at_level(logging.DEBUG, logger="vt.test.debug"):
        logger.debug("dbg")
    assert any(r.levelno == logging.DEBUG and r.name == "vt.test.debug" for r in caplog.records)

def test_no_duplicate_handlers():
    """Calling get_logger twice for the same name should NOT add extra handlers."""
    logger1 = get_logger("vt.test.dup", "INFO")
    count1 = len(logger1.handlers)
    logger2 = get_logger("vt.test.dup", "INFO")
    count2 = len(logger2.handlers)
    assert count1 == count2 == 1  # only one handler
