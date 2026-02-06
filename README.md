# NVDA vs AMZN Streamlit Dashboard

Compare NVIDIA (NVDA) and Amazon (AMZN) with public market data, fundamentals, and financial statements using Streamlit + yfinance.

## Features
- Market performance charts and KPIs
- Fundamentals comparison table
- Annual and quarterly financial charts with CSV download
- Optional news headlines (when available via yfinance)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Notes
- Data is provided by yfinance and may be delayed or incomplete.
- The app caches downloads with `st.cache_data` to keep it fast.
