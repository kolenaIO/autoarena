import os
from contextlib import contextmanager
from typing import Iterator


@contextmanager
def unset_environment_variable(key: str) -> Iterator[None]:
    prev = os.environ.get(key, None)
    if prev is not None:
        del os.environ[key]
    yield
    if prev is not None:
        os.environ[key] = prev


@contextmanager
def temporary_environment_variable(key: str, value: str) -> Iterator[None]:
    prev = os.environ.get(key, None)
    os.environ[key] = value
    yield
    if prev is not None:
        os.environ[key] = prev
