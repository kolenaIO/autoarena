from io import StringIO

import httpx
import pandas as pd


def upload_model_responses(project_slug: str, model_name: str, df_response: pd.DataFrame) -> dict:
    filename = f"{model_name}.csv"
    buffer = StringIO()
    df_response.to_csv(buffer, index=False)
    buffer.seek(0)
    data = {f"{filename}||model_name": model_name}
    files = {filename: (filename, buffer.read())}
    response = httpx.post(f"/project/{project_slug}/model", data=data, files=files)
    return response.json()
