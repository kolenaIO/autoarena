import time
from io import StringIO

import pytest
from loguru import logger
from pytimeparse.timeparse import timeparse

from autoarena.judge.openai import OpenAIJudge


def test__judge__openai__handle_rate_limit() -> None:
    headers = {
        "x-ratelimit-remaining-requests": "10",
        "x-ratelimit-remaining-tokens": "1000",
        "x-ratelimit-reset-requests": "20h0m29.594s",
        "x-ratelimit-reset-tokens": "0.1s",
    }
    log_stream = StringIO()
    logger.add(log_stream)
    t0 = time.time()
    OpenAIJudge._handle_rate_limit(headers)
    t1 = time.time()
    log_stream.seek(0)
    logs = log_stream.read()
    assert "Approaching OpenAI request rate limit" in logs
    assert "Approaching OpenAI token rate limit" in logs
    assert t1 - t0 > timeparse(headers["x-ratelimit-reset-tokens"])


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"x-ratelimit-remaining-requests": "abc", "x-ratelimit-remaining-tokens": "abc"},
        {
            "x-ratelimit-remaining-requests": "123",
            "x-ratelimit-remaining-tokens": "123",
            "x-ratelimit-reset-requests": "20h0m29.594s",
            "x-ratelimit-reset-tokens": "somehow invalid",
        },
    ],
)
def test__judge__openai__handle_rate_limit__failed(headers: dict[str, str]) -> None:
    OpenAIJudge._handle_rate_limit(headers)  # should not crash if the headers are malformed or missing
