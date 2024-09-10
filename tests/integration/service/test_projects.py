import pytest

from autoarena.error import NotFoundError
from autoarena.service.project import ProjectService


def test__connect__failed() -> None:
    with pytest.raises(NotFoundError):
        with ProjectService.connect("does-not-exist"):
            ...
