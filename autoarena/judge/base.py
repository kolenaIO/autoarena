import os
from abc import abstractmethod, ABCMeta
from typing import Optional

from loguru import logger


class AutomatedJudge(metaclass=ABCMeta):
    API_KEY_NAME: Optional[str] = None  # if set, verify that this exists in environment on init
    MAX_TOKENS = 12  # should really just need one or two

    _model_name: str
    _system_prompt: str

    n_calls: int
    total_input_tokens: int
    total_output_tokens: int

    def __init__(self, model_name: str, system_prompt: str):
        self._model_name = model_name
        self._system_prompt = system_prompt
        self.n_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        key = os.environ.get(self.API_KEY_NAME, None) if self.API_KEY_NAME is not None else None
        if self.API_KEY_NAME is not None and key is None:
            message = f"API key '{self.API_KEY_NAME}' must be set in environment running AutoArena to use '{self.name}'"
            raise RuntimeError(message)

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @abstractmethod
    def judge(self, prompt: str, response_a: str, response_b: str) -> str:
        raise NotImplementedError

    @staticmethod
    def verify_environment() -> None:
        """
        Verify that the current environment contains any necessary configuration, such as API keys, necessary to
        interact with this judge. Throw an exception if not.
        """

    def log_usage(self) -> None:
        logger.info(
            f"'{self.name}' used {self.total_input_tokens} input tokens and {self.total_output_tokens} output tokens "
            f"over {self.n_calls} calls",
        )
