import os
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from api import AskLLM, ModelChoice

load_dotenv(os.path.join(os.getcwd(), ".env"), override=True)

api_keys = {
    "COHERE": os.getenv("COHERE_API_KEY"),
    "ANTHROPIC": os.getenv("ANTHROPIC_API_KEY"),
    "OPENAI": os.getenv("OPENAI_API_KEY"),
    "GOOGLE": os.getenv("GOOGLE_API_KEY"),
    "TOGETHER": os.getenv("TOGETHER_API_KEY"),
}

valid_api_keys = {key: value for key, value in api_keys.items() if value and value != "abc123"}

model_map = {
    "COHERE": [ModelChoice.command_r_08_2024],
    "ANTHROPIC": [ModelChoice.claude_3_5_sonnet_20240620],
    "OPENAI": [ModelChoice.o1_mini, ModelChoice.o1_preview, ModelChoice.gpt_4o_mini, ModelChoice.gpt_4o],
    "GOOGLE": [ModelChoice.gemini_1_5_pro_002],
    "TOGETHER": [ModelChoice.llama_3_2_90B],
}

model_choices = [model for key, models in model_map.items() if key in valid_api_keys for model in models]

print("Models to generate answers on:\n" + "\n".join(model_choices))

os.makedirs("models", exist_ok=True)

df = pd.read_csv("TruthfulQA.csv", usecols=["Question"])

for model_choice in model_choices:
    file = f"models/{model_choice}.csv"

    if os.path.exists(file):
        # Skip if this model's responses have already been saved
        continue

    llm_instance = AskLLM(model_choice, valid_api_keys)

    results = []

    for index, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing rows for {model_choice}"):
        question = row["Question"]
        try:
            response = llm_instance.get_api_result(question)
            results.append({"prompt": question, "response": response})
        except Exception as e:
            results.append({"prompt": question, "response": "<MODEL API ERROR>"})
            print(e)

    result_df = pd.DataFrame(results)
    result_df.to_csv(file, index=False)
    print(f"Results saved to {file}")
