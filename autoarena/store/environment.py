import os
from abc import ABCMeta, abstractmethod


class KeyManager(metaclass=ABCMeta):
    @abstractmethod
    def get(self, key: str) -> str:
        """Retrieve the value for the provided key from the environment."""


class OsEnvironKeyManager(KeyManager):
    def get(self, key: str) -> str:
        return os.environ[key]
