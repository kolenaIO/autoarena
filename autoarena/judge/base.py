import os
from abc import abstractmethod, ABCMeta
from typing import Optional

import numpy as np
from loguru import logger


class AutomatedJudge(metaclass=ABCMeta):
    API_KEY_NAME: Optional[str] = None  # if set, verify that this exists in environment on init
    MAX_TOKENS: int = 12  # should really just need one or two
    SLOW_THRESHOLD_SECONDS: float = 5

    _name: str
    _model_name: str
    _system_prompt: str

    n_requests: int
    total_input_tokens: int
    total_output_tokens: int
    response_seconds: list[float]

    def __init__(self, name: str, model_name: str, system_prompt: str):
        self._name = name
        self._model_name = model_name
        self._system_prompt = system_prompt
        self.n_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.response_seconds = []
        key = os.environ.get(self.API_KEY_NAME, None) if self.API_KEY_NAME is not None else None
        if self.API_KEY_NAME is not None and key is None:
            message = f"API key '{self.API_KEY_NAME}' must be set in environment running AutoArena to use '{self.name}'"
            raise RuntimeError(message)

    @property
    def name(self) -> str:
        return self._name

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

    def update_usage(self, input_tokens: int, output_tokens: int, response_seconds: float) -> None:
        """Optionally call in `AutomatedJudge.judge` implementations to record usage metrics."""
        self.n_requests += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.response_seconds.append(response_seconds)
        if response_seconds >= self.SLOW_THRESHOLD_SECONDS:
            logger.warning(f"Slow response from '{self.name}': {response_seconds:0.3f} seconds")

    def get_usage_summary(self) -> list[str]:
        if self.n_requests == 0 or len(self.response_seconds) == 0:
            return [f"'{self.name}' has not recorded any usage"]
        return [
            f"'{self.name}' used {self.total_input_tokens} input tokens and {self.total_output_tokens} output tokens "
            f"over {self.n_requests} requests",
            f"  * p50 latency: {np.percentile(self.response_seconds, 50):0.3f} seconds",
            f"  * p90 latency: {np.percentile(self.response_seconds, 90):0.3f} seconds",
            f"  * p99 latency: {np.percentile(self.response_seconds, 99):0.3f} seconds",
        ]
