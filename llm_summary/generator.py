import os
from dotenv import load_dotenv
load_dotenv()

from openai import AzureOpenAI


# openai_model = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-mini")
# api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
# azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
# api_key = os.getenv("AZURE_OPENAI_KEY")


openai_model = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-mini")
api_version = os.getenv("OPENAI_API_VERSION", "2024-12-01-preview")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    azure_deployment=openai_model,
    api_key=api_key,
)

def generate_llm_summary(prompt: str, callback=None) -> str:
    try:
        completion = client.chat.completions.create(
            model=openai_model,
            messages=[{"role": "user", "content": prompt}]
        )
        result = completion.choices[0].message.content
        if callback:
            callback(result)
        return result
    except Exception as e:
        return f"LLM generation failed: {e}"