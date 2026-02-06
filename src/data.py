from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import streamlit as st
import yfinance as yf


@dataclass
class FinancialStatement:
    annual: pd.DataFrame
    quarterly: pd.DataFrame


@st.cache_data(show_spinner=False)
def get_price_history(
    tickers: Iterable[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    interval: str = "1d",
) -> pd.DataFrame:
    symbols = list(dict.fromkeys([t.upper() for t in tickers]))
    if not symbols:
        return pd.DataFrame()
    data = yf.download(
        tickers=symbols,
        start=start,
        end=end,
        interval=interval,
        group_by="ticker",
        auto_adjust=False,
        progress=False,
        threads=True,
    )
    if data.empty:
        return data
    if isinstance(data.columns, pd.MultiIndex):
        close_frames = []
        for symbol in symbols:
            if symbol in data.columns.get_level_values(0):
                close = data[symbol]["Close"].rename(symbol)
                close_frames.append(close)
        if close_frames:
            return pd.concat(close_frames, axis=1).dropna(how="all")
        return pd.DataFrame()
    return data[["Close"]].rename(columns={"Close": symbols[0]})


@st.cache_data(show_spinner=False)
def get_company_info(tickers: Iterable[str]) -> pd.DataFrame:
    info_rows = []
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
        except Exception:
            info = {}
        info_rows.append({"ticker": symbol, **info})
    if not info_rows:
        return pd.DataFrame()
    return pd.DataFrame(info_rows).set_index("ticker")


@st.cache_data(show_spinner=False)
def get_financials(tickers: Iterable[str]) -> dict[str, FinancialStatement]:
    financials: dict[str, FinancialStatement] = {}
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            annual = ticker.financials
            quarterly = ticker.quarterly_financials
        except Exception:
            annual = pd.DataFrame()
            quarterly = pd.DataFrame()
        financials[symbol] = FinancialStatement(annual=annual, quarterly=quarterly)
    return financials


@st.cache_data(show_spinner=False)
def get_news(tickers: Iterable[str]) -> dict[str, list[dict]]:
    news: dict[str, list[dict]] = {}
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            news_items = ticker.news or []
        except Exception:
            news_items = []
        news[symbol] = news_items
    return news
