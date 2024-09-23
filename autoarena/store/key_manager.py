import os
from abc import ABCMeta, abstractmethod
from contextvars import ContextVar


class KeyManager(metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str) -> str:
        """Retrieve the value for the provided key."""


class OsEnvironKeyManager(KeyManager):
    def get(self, key: str) -> str:
        return os.environ[key]


KeyManagerProvider: ContextVar[KeyManager] = ContextVar("_KEY_MANAGER", default=OsEnvironKeyManager())
