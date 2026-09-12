from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
load_dotenv()
import os

groq_model_name = "meta-llama/llama-4-scout-17b-16e-instruct"

llm_model = LiteLlm(model=f"groq/{groq_model_name}")

MODEL = os.getenv("MODEL")