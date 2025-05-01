import pandas as pd
from .generator import generate_llm_summary
from .formatter import build_prompt, html_to_plain
from .model_utils import extract_forecast_data

def run_summary_pipeline(year: int, region: str, df: pd.DataFrame) -> dict:
    data = extract_forecast_data(df, year, region)
    prompt = build_prompt(year, region, data)
    html_response = generate_llm_summary(prompt)
    plain_response = html_to_plain(html_response)


      # 🔍 Print for debugging
    print("------ LLM PROMPT SENT ------")
    print(prompt)
    print("------ LLM HTML RESPONSE ------")
    print(html_response)
    print("------ LLM PLAIN RESPONSE ------")
    print(plain_response)

    return {
        "html": html_response,
        "plain": plain_response,
        "prompt": prompt,
    }

if __name__ == "__main__":
    df = pd.read_csv("output_mock.csv")
    year = 2031
    region = "Hartlepool"

    result = run_summary_pipeline(year, region, df)

    print("\n--- HTML Output ---\n", result["html"])
    print("\n--- Plain Text Fallback ---\n", result["plain"])
