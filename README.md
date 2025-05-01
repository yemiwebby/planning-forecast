# 🏘️ Planning Forecast By Team 5

**Planning Forecast** is a smart dashboard designed to support UK local authorities with data-driven housing strategy.  
It combines predictive housing data with multi-step, agentic AI reasoning to generate actionable insights — not just answers.

## Overview

The planning system struggles to meet the demand for new housing and anticipate future demand. There is an opportunity to develop predictive models that can integrate population trends, migration patterns, and economic indicators to improve forecasting and support data-driven decision-making in housing supply needs.

Local governments often struggle with fragmented housing data, complex forecasting, and limited resources to interpret it.  
**Planning Forecast** solves this by combining:

- 📈 Predictive data on housing prices, affordability, and supply
- 🧠 Multi-step AI analysis using Azure OpenAI
- 🗺️ Interactive visualizations and maps
- 📋 Summaries designed for planning officers, not just data scientists

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Agentic Workflow](#agentic-workflow)
- [Design Decisions](#design-decisions)
- [Setup Instructions](#setup-instructions)
- [Future Enhancements](#future-enhancements)
- [Contributors](#contributors)

## Features

- Forecasts for:
  - 🏠 Housing Price
  - 📊 Housing Affordability Index
  - 🏗️ Net Additional Dwellings
- Interactive map and timeseries visualizations
- Agentic AI summary generator using Azure OpenAI
- Clean UI built with Dash (Flask + React)
- Summary explanations rendered in structured HTML
- Automated summary ready for local authority reports

---

## Tech Stack

| Layer           | Technology                  |
| --------------- | --------------------------- |
| Frontend UI     | Dash (Plotly + React)       |
| Data Handling   | Pandas, GeoPandas           |
| Mapping         | Folium (Leaflet.js wrapper) |
| LLM Integration | Azure OpenAI (GPT-4.1-mini) |
| Agent Framework | Manual prompt chaining      |
| Deployment      | Localhost / Any cloud-ready |

---

## How It Works

1. User selects:
   - A Local Authority (e.g., Derby)
   - A forecast year (e.g., 2026)
   - A metric (e.g., Affordability)
2. The app loads relevant predictive data and visualizes it.
3. A **multi-step LLM agent** (not just a single prompt) produces:
   - A localized forecast summary
   - A comparison against national averages
   - A recommendation for local housing policy

---

## Agentic Workflow

Unlike a chatbot, our LLM is structured as a **goal-driven assistant**. Here's how the agent works:

### Goal:

Generate a meaningful planning recommendation for a selected LA + year.

### Steps:

1. **Forecast Summary Agent**  
   Describes expected housing price, affordability, and supply.
2. **Comparison Agent**  
   Compares local stats to national averages, explaining differences.
3. **Advisor Agent**  
   Suggests 1–2 planning actions based on challenges identified.

Each step feeds its result into the next — enabling reasoning and refinement.

> 🔁 This is not a chatbot. It's a composed agentic process — a planner that thinks in steps.

---

## Predictive Model Usage

- We simulate real housing forecasts using structured data fields like:
  - `2031_housing_price`
  - `2031_housing_affordability_ci_upper`
- The data includes:
  - Forecast values
  - Confidence intervals
  - Local Authority codes (LAD23CD) and names

These are ingested, cleaned, and summarized via the agent pipeline.

---

## Setup Instructions

1. **Clone the project**
   ```bash
   git clone https://github.com/your-org/planning-forecast.git
   cd planning-forecast
   ```
2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Add your `.env` file** with Azure OpenAI credentials:
   ```ini
   AZURE_OPENAI_MODEL=gpt-4.1-mini
   OPENAI_API_VERSION=2024-12-01-preview
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=sk-xxxxxxxxxxxxxxxxxxxx
   ```
5. **Run the app**
   ```bash
   python dash_llm_app/app.py
   ```
6. **Access the app** at `http://

## Design Decisions

- We avoided frameworks like Streamlit to allow for:

  - Full UI customization with Dash

  - Scalable deployment via Flask

- The LLM logic is modular (llm_summary/) and testable

- Summary content is HTML-safe and scrollable

- We prioritize planning officers as the end user — not developers

## Future Enhancements

- 📋 Copy-to-Clipboard (JS-free fallback in progress)

- 📄 PDF Export

- 🧠 Scenario Simulation (What-if housing demands)

- ☁️ Cloud Deployment (AWS, Azure App Service, or Streamlit Cloud)

- 🧪 Unit Tests for agent steps

- 🗂️ Upload custom datasets (e.g., SHLAA, economic zones)

## Contributors

- Iman Bakhit
- James Campbell
- Bashir Abubakar
- Benjamin Lambe
- Oluyemi Olususi
- Ricky Nathvani
- Ruby Johnson
