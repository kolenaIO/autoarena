import tempfile
from pathlib import Path

import pandas as pd

from autoarena.api import api
from autoarena.main import main
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.model import ModelService
from autoarena.service.project import ProjectService


def test__cli__seed(test_data_directory: Path) -> None:
    h2h_records = [
        dict(model_a="a", model_b="b", prompt="example", response_a="response a", response_b="response b", winner="-"),
        dict(model_a="b", model_b="a", prompt="another", response_a="from b", response_b="from a", winner="A"),
        dict(model_a="c", model_b="a", prompt="vs. c", response_a="from c", response_b="from a", winner="A"),
    ]
    df_h2h_input = pd.DataFrame.from_records(h2h_records)
    with tempfile.NamedTemporaryFile(suffix=".csv") as f:
        filename = f.name
        df_h2h_input.to_csv(f, index=False)
        main(["seed", filename])

    projects = ProjectService.get_all()
    project_slug = Path(filename).stem
    assert len(projects) == 1
    assert projects[0].slug == project_slug

    models = ModelService.get_all(project_slug)
    assert {m.name for m in models} == set(df_h2h_input.model_a) | set(df_h2h_input.model_b)
    for model in models:
        assert model.n_responses > 0
        assert model.n_votes > 0
        assert model.q025 is not None
        assert model.q975 is not None
        df_h2h_model = HeadToHeadService.get_df(project_slug, api.HeadToHeadsRequest(model_a_id=model.id))
        df_h2h_input_model = df_h2h_input[(df_h2h_input.model_a == model.name) | (df_h2h_input.model_b == model.name)]
        assert len(df_h2h_model) == len(df_h2h_input_model)
        assert all(df_h2h_model.history.apply(lambda h: len(h) == 1))
        assert all(df_h2h_model.history.apply(lambda h: h[0]["judge_name"] == "Human"))
