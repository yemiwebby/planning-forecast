# Planning Forecast

**Planning Forecast** is a forecasting dashboard for UK local authorities. It combines predictive housing data with LLM-powered narrative summaries to support planning and decision-making.

## Features

- View forecasts for housing price, affordability, and dwellings
- Interactive maps and graphs
- Natural-language summaries generated using Azure OpenAI

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Ensure your `.env` file is configured with your Azure OpenAI credentials.

AZURE_OPENAI_MODEL=gpt-4.1-mini
OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_ENDPOINT=YOUR_ENDPOINT
AZURE_OPENAI_KEY=YOUR_AZURE_OPENAI_KEY
