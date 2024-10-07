import os
import gdown
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from api import AskLLM, Model

load_dotenv(os.path.join(os.getcwd(), ".env"), override=True)

api_keys = {
    "COHERE": os.getenv("COHERE_API_KEY"),
    "ANTHROPIC": os.getenv("ANTHROPIC_API_KEY"),
    "OPENAI": os.getenv("OPENAI_API_KEY"),
    "GOOGLE": os.getenv("GOOGLE_API_KEY"),
    "TOGETHER": os.getenv("TOGETHER_API_KEY"),
}

model_map = {
    "COHERE": [Model.command_r_08_2024],
    "ANTHROPIC": [Model.claude_3_5_sonnet_20240620],
    "OPENAI": [Model.o1_mini, Model.o1_preview, Model.gpt_4o_mini, Model.gpt_4o],
    "GOOGLE": [Model.gemini_1_5_pro_002],
    "TOGETHER": [Model.llama_3_2_90B],
}

drive_file_urls = {
    "TruthfulQA": "https://drive.google.com/uc?export=download&id=1bT-fEmaP2G7-oHbFtUu9SMaIzo0CJToH",
    Model.command_r_08_2024: "https://drive.google.com/uc?export=download&id=1QeNUN3OilU_lvhY08yDw0IGYmu0mObi3",
    Model.claude_3_5_sonnet_20240620: "https://drive.google.com/uc?export=download&id=1JbutQpx9A37yfyF20DIjS5Xhh1_cpgAf",
    Model.o1_mini: "https://drive.google.com/uc?export=download&id=19WgQ76sWamtNY5LN7cCEqWecudkAWQjF",
    Model.o1_preview: "https://drive.google.com/uc?export=download&id=1c00To5UCY1OeBFWN2i-VpE_lF9VTWufa",
    Model.gpt_4o_mini: "https://drive.google.com/uc?export=download&id=13PsSpYNUcrN3LzpmO2xTyGBwgJ9w-Dmh",
    Model.gpt_4o: "https://drive.google.com/uc?export=download&id=1I6WAHexfFJM84_GeDyc_MQ56YhfKLG0w",
    Model.gemini_1_5_pro_002: "https://drive.google.com/uc?export=download&id=1kAroyO6_j9AGun3Q7Kv4gGMbnVl5CHY1",
    Model.llama_3_2_90B: "https://drive.google.com/uc?export=download&id=1KZVwr1UM51o8Bs5-RAKK_66kywAGhQq4",
}


os.makedirs("models", exist_ok=True)
valid_api_keys = {key: value for key, value in api_keys.items() if value and value != "abc123"}
model_choices = [model for key, models in model_map.items() if key in valid_api_keys for model in models]


# Download model responses to skip generation in absence of certian API keys

for model_choice, file in drive_file_urls.items():
    file_path = f"models/{model_choice}.csv"
    if model_choice not in model_choices and not os.path.exists(file_path) and model_choice != "TruthfulQA":
        print(f"Downloading {model_choice} results...")
        gdown.download(file, file_path, quiet=True)
        print(f"Results saved to {file_path}")


# Download the original TruthfulQA dataset
dataset_path = "TruthfulQA.csv"
if not os.path.exists(dataset_path):
    print("Downloading the TruthfulQA dataset...")
    gdown.download(drive_file_urls["TruthfulQA"], dataset_path, quiet=True)
    df = pd.read_csv(dataset_path, usecols=["Question"])
    print(f"TruthfulQA saved to {dataset_path}")


# Generate responses from scratch if the relevant API keys are provided

if model_choices:
    print("Models to generate answers on:\n" + "\n".join(model_choices))

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
