from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from src.charts import build_bar_chart, build_normalized_chart, build_price_chart
from src.data import get_company_info, get_financials, get_news, get_price_history
from src.metrics import (
    compute_cumulative_returns,
    compute_latest_kpis,
    compute_returns,
    compute_volatility,
)

st.set_page_config(page_title="NVDA vs AMZN Dashboard", layout="wide")

st.title("NVIDIA vs Amazon Dashboard")

with st.sidebar:
    st.header("Controls")
    selected_tickers = st.multiselect(
        "Tickers", options=["NVDA", "AMZN", "SPY"], default=["NVDA", "AMZN"]
    )
    include_benchmark = st.checkbox("Include SPY benchmark", value=False)
    if include_benchmark and "SPY" not in selected_tickers:
        selected_tickers.append("SPY")

    start_date = st.date_input("Start date", value=date(2020, 1, 1))
    end_date = st.date_input("End date", value=date.today())
    frequency = st.selectbox("Frequency", options=["1d", "1wk"], index=0)

if not selected_tickers:
    st.info("Select at least one ticker to begin.")
    st.stop()

prices = get_price_history(
    selected_tickers, start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), interval=frequency
)

market_tab, fundamentals_tab, financials_tab, news_tab = st.tabs(
    ["Market", "Fundamentals", "Financials", "News"]
)

with market_tab:
    st.subheader("Market Overview")
    if prices.empty:
        st.warning("Price data is unavailable for the selected tickers/date range.")
    else:
        st.plotly_chart(build_price_chart(prices), use_container_width=True)
        cumulative = compute_cumulative_returns(prices)
        st.plotly_chart(build_normalized_chart(cumulative), use_container_width=True)

        returns = compute_returns(prices)
        volatility = compute_volatility(returns, periods_per_year=252 if frequency == "1d" else 52)
        kpis = compute_latest_kpis(prices)
        kpis["annualized_volatility"] = volatility

        st.subheader("Key Metrics")
        st.dataframe(
            kpis.style.format(
                {
                    "latest_price": "${:,.2f}",
                    "total_return": "{:.2%}",
                    "latest_return": "{:.2%}",
                    "max_drawdown": "{:.2%}",
                    "annualized_volatility": "{:.2%}",
                }
            ),
            use_container_width=True,
        )

with fundamentals_tab:
    st.subheader("Fundamentals")
    info = get_company_info(selected_tickers)
    if info.empty:
        st.warning("Fundamental data is unavailable.")
    else:
        fields = [
            "longName",
            "sector",
            "industry",
            "marketCap",
            "trailingPE",
            "forwardPE",
            "dividendYield",
            "profitMargins",
            "returnOnEquity",
        ]
        display_info = info.reindex(columns=fields)
        display_info = display_info.rename(
            columns={
                "longName": "Company",
                "marketCap": "Market Cap",
                "trailingPE": "Trailing P/E",
                "forwardPE": "Forward P/E",
                "dividendYield": "Dividend Yield",
                "profitMargins": "Profit Margin",
                "returnOnEquity": "Return on Equity",
            }
        )
        st.dataframe(display_info, use_container_width=True)

with financials_tab:
    st.subheader("Financial Statements")
    financials = get_financials(selected_tickers)

    def extract_line_item(statements, label):
        frames = {}
        for ticker, statement in statements.items():
            data = statement.get(label, pd.Series(dtype=float))
            if not data.empty:
                frames[ticker] = data
        if not frames:
            return pd.DataFrame()
        df = pd.DataFrame(frames).sort_index()
        df.index = pd.to_datetime(df.index).date
        return df

    annual_statements = {k: v.annual for k, v in financials.items()}
    quarterly_statements = {k: v.quarterly for k, v in financials.items()}

    annual_revenue = extract_line_item(annual_statements, "Total Revenue")
    annual_income = extract_line_item(annual_statements, "Net Income")
    quarterly_revenue = extract_line_item(quarterly_statements, "Total Revenue")
    quarterly_income = extract_line_item(quarterly_statements, "Net Income")

    if annual_revenue.empty and quarterly_revenue.empty:
        st.warning("Financial statement data is unavailable.")
    else:
        if not annual_revenue.empty:
            st.plotly_chart(
                build_bar_chart(annual_revenue, "Annual Revenue", "USD"),
                use_container_width=True,
            )
            st.plotly_chart(
                build_bar_chart(annual_income, "Annual Net Income", "USD"),
                use_container_width=True,
            )
        if not quarterly_revenue.empty:
            st.plotly_chart(
                build_bar_chart(quarterly_revenue, "Quarterly Revenue", "USD"),
                use_container_width=True,
            )
            st.plotly_chart(
                build_bar_chart(quarterly_income, "Quarterly Net Income", "USD"),
                use_container_width=True,
            )

        combined = {
            "annual_revenue": annual_revenue,
            "annual_net_income": annual_income,
            "quarterly_revenue": quarterly_revenue,
            "quarterly_net_income": quarterly_income,
        }
        csv_data = pd.concat(combined, names=["statement", "date"]).reset_index()
        st.download_button(
            "Download financials CSV",
            csv_data.to_csv(index=False).encode("utf-8"),
            file_name="financials.csv",
            mime="text/csv",
        )

with news_tab:
    st.subheader("Latest News")
    news_items = get_news(selected_tickers)
    has_news = False
    for ticker, items in news_items.items():
        if not items:
            continue
        has_news = True
        st.markdown(f"**{ticker}**")
        for item in items[:5]:
            title = item.get("title", "Headline")
            link = item.get("link", "")
            publisher = item.get("publisher", "")
            if link:
                st.markdown(f"- [{title}]({link}) ({publisher})")
            else:
                st.markdown(f"- {title} ({publisher})")
    if not has_news:
        st.info("News is not available. You can add a custom provider later if needed.")
