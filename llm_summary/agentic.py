from .formatter import build_prompt, html_to_plain
from .generator import generate_llm_summary
from .model_utils import extract_forecast_data
import pandas as pd

def run_agentic_summary(year: int, region: str, df: pd.DataFrame) -> dict:
    # Step 1: Summarize forecast for selected region
    forecast_data = extract_forecast_data(df, year, region)
    step1_prompt = build_prompt(year, region, forecast_data)

    print("\n📝 STEP 1 PROMPT:\n", step1_prompt)
    step1_response = generate_llm_summary(step1_prompt)
    print("\n🔹 STEP 1: Forecast Summary\n", step1_response)

    # Step 2: Compare to national average
    national_avg_price = df[f"{year}_housing_price"].mean()
    regional_price = forecast_data["housing_price"]
    step2_prompt = f"""
Given the following summary for {region} in {year}:

{step1_response}

The forecasted housing price for {region} is £{regional_price:,}, while the national average is £{int(national_avg_price):,}.

Please compare this region to the national average and explain what that may indicate in terms of housing demand or affordability challenges.

Keep your response under 100 words and format with <p> and <b> tags.
"""
    step2_response = generate_llm_summary(step2_prompt)
    print("\n🔹 STEP 2: Comparison\n", step2_response)

    # Step 3: Recommend a planning action
    step3_prompt = f"""
Based on the forecast and regional comparison below:

Forecast Summary:
{step1_response}

Comparison Insight:
{step2_response}

Now suggest 1 or 2 planning actions the local authority should consider in response. 
Think like a housing strategy advisor. Use <p> and <b> tags. Keep it clear and professional.
"""
    step3_response = generate_llm_summary(step3_prompt)
    print("\n🔹 STEP 3: Recommendation\n", step3_response)

    # ✅ Final output — cleanly formatted for Dash Markdown rendering
    final_output = f"""
<b>1. Forecast Summary</b><br>
{step1_response.replace('<p>', '').replace('</p>', '<br>')}<br><br>

<b>2. Comparison to National Average</b><br>
{step2_response.replace('<p>', '').replace('</p>', '<br>')}<br><br>

<b>3. Planning Recommendations</b><br>
{step3_response.replace('<p>', '').replace('</p>', '<br>')}<br>
"""

    return {
        "html": final_output,
        "steps": [step1_response, step2_response, step3_response]
    }
