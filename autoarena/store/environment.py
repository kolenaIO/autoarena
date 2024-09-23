import os
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator


class KeyManager(metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str) -> str:
        """Retrieve the value for the provided key."""


class OsEnvironKeyManager(KeyManager):
    def get(self, key: str) -> str:
        return os.environ[key]


_KEY_MANAGER: ContextVar[KeyManager] = ContextVar("_KEY_MANAGER", default=OsEnvironKeyManager())


class KeyManagerProvider:
    @staticmethod
    @contextmanager
    def set(key_manager: KeyManager) -> Iterator[KeyManager]:
        _KEY_MANAGER.set(key_manager)
        yield key_manager

    @staticmethod
    def get() -> KeyManager:
        return _KEY_MANAGER.get()
