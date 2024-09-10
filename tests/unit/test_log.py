import logging
from io import StringIO
from pathlib import Path

from loguru import logger

from autoarena.log import InterceptHandler


def test__intercept_handler() -> None:
    handler = InterceptHandler()
    record = logging.LogRecord(
        name="test__intercept_handler",
        level=logging.INFO,
        pathname=str(Path(__file__)),
        lineno=23,
        msg="Intercept handler test: %s",
        args=("testing",),
        exc_info=None,
    )
    logs = StringIO()
    logger.add(logs)
    handler.emit(record)
    logs.seek(0)
    log = logs.read()
    assert record.name in log
    assert record.msg % record.args in log
