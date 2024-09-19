import pandas as pd

from autoarena.api import api
from autoarena.service.head_to_head import HeadToHeadService
from autoarena.service.judge import JudgeService
from autoarena.service.model import ModelService


# verify that winner is correct if an existing H2H record is replaced with a record with opposite ordered response_ids
def test__head_to_head__upload__replace(project_slug: str) -> None:
    df_a = pd.DataFrame([("p", "ra")], columns=["prompt", "response"])
    model_a = ModelService.upload_responses(project_slug, "model_a", df_a)
    df_b = pd.DataFrame([("p", "rb")], columns=["prompt", "response"])
    model_b = ModelService.upload_responses(project_slug, "model_b", df_b)

    create_judge_request = api.CreateJudgeRequest(
        judge_type=api.JudgeType.CUSTOM,
        name="custom-tester",
        model_name="tester",
        system_prompt="unimportant",
        description="also unimportant",
    )
    judge = JudgeService.create(project_slug, create_judge_request)
    responses_a = ModelService.get_df_response(project_slug, model_a.id)
    responses_b = ModelService.get_df_response(project_slug, model_b.id)
    assert len(responses_a) == len(responses_b) == 1

    df_h2h_input = pd.DataFrame(
        [(responses_a.iloc[0].response_id, responses_b.iloc[0].response_id, judge.id, "A")],
        columns=["response_a_id", "response_b_id", "judge_id", "winner"],
    )

    def verify_df_h2h_retrieved(df_h2h_retrieved: pd.DataFrame) -> None:
        assert len(df_h2h_retrieved) == len(df_h2h_input) == 1
        assert df_h2h_retrieved.iloc[0].response_a_id == df_h2h_input.iloc[0].response_a_id
        assert df_h2h_retrieved.iloc[0].response_b_id == df_h2h_input.iloc[0].response_b_id
        assert df_h2h_retrieved.iloc[0].history == [dict(judge_id=judge.id, judge_name=judge.name, winner="A")]

    HeadToHeadService.upload_head_to_heads(project_slug, df_h2h_input)
    head_to_heads_request = api.HeadToHeadsRequest(model_a_id=model_a.id, model_b_id=model_b.id)
    verify_df_h2h_retrieved(HeadToHeadService.get_df(project_slug, head_to_heads_request))

    df_h2h_input_flipped = pd.DataFrame(  # still a vote for the same winner, just in a different order
        [(responses_b.iloc[0].response_id, responses_a.iloc[0].response_id, judge.id, "B")],
        columns=["response_a_id", "response_b_id", "judge_id", "winner"],
    )
    HeadToHeadService.upload_head_to_heads(project_slug, df_h2h_input_flipped)
    verify_df_h2h_retrieved(HeadToHeadService.get_df(project_slug, head_to_heads_request))

    # vote again for the original winner and ensure it's still correct
    HeadToHeadService.upload_head_to_heads(project_slug, df_h2h_input)
    verify_df_h2h_retrieved(HeadToHeadService.get_df(project_slug, head_to_heads_request))
