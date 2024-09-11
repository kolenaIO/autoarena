import inspect
import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercept standard library log messages and emit via Loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        """See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging"""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def initialize_logger() -> None:
    # replace uvicorn loggers with InterceptHandler
    intercept_handler = InterceptHandler()
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict if name.startswith("uvicorn.")]
    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []
    logging.getLogger("uvicorn").handlers = [intercept_handler]
    logging.getLogger("uvicorn.access").handlers = [intercept_handler]
