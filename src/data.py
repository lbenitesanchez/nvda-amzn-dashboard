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
def _fetch_price_history(
    tickers: Iterable[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    interval: str = "1d",
) -> tuple[pd.DataFrame, pd.Timestamp]:
    symbols = list(dict.fromkeys([t.upper() for t in tickers]))
    if not symbols:
        return pd.DataFrame(), pd.Timestamp.utcnow()
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
        return data, pd.Timestamp.utcnow()
    if isinstance(data.columns, pd.MultiIndex):
        close_frames = []
        for symbol in symbols:
            if symbol in data.columns.get_level_values(0):
                close = data[symbol]["Close"].rename(symbol)
                close_frames.append(close)
        if close_frames:
            return pd.concat(close_frames, axis=1).dropna(how="all"), pd.Timestamp.utcnow()
        return pd.DataFrame(), pd.Timestamp.utcnow()
    return data[["Close"]].rename(columns={"Close": symbols[0]}), pd.Timestamp.utcnow()


def get_price_history(
    tickers: Iterable[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    interval: str = "1d",
) -> tuple[pd.DataFrame, pd.Timestamp, bool]:
    data, fetched_at = _fetch_price_history(tickers, start, end, interval)
    cached = pd.Timestamp.utcnow() - fetched_at > pd.Timedelta(seconds=5)
    return data, fetched_at, cached


@st.cache_data(show_spinner=False)
def _fetch_company_info(tickers: Iterable[str]) -> tuple[dict[str, dict], pd.Timestamp]:
    info_rows: dict[str, dict] = {}
    for symbol in tickers:
        ticker = yf.Ticker(symbol)
        info_rows[symbol] = ticker.info or {}
    return info_rows, pd.Timestamp.utcnow()


def get_company_info(tickers: Iterable[str]) -> tuple[dict[str, dict], pd.Timestamp, bool]:
    info_rows, fetched_at = _fetch_company_info(tickers)
    cached = pd.Timestamp.utcnow() - fetched_at > pd.Timedelta(seconds=5)
    return info_rows, fetched_at, cached


@st.cache_data(show_spinner=False)
def _fetch_financials(tickers: Iterable[str]) -> tuple[dict[str, FinancialStatement], pd.Timestamp]:
    financials: dict[str, FinancialStatement] = {}
    for symbol in tickers:
        ticker = yf.Ticker(symbol)
        annual = ticker.financials
        quarterly = ticker.quarterly_financials
        financials[symbol] = FinancialStatement(annual=annual, quarterly=quarterly)
    return financials, pd.Timestamp.utcnow()


def get_financials(tickers: Iterable[str]) -> tuple[dict[str, FinancialStatement], pd.Timestamp, bool]:
    financials, fetched_at = _fetch_financials(tickers)
    cached = pd.Timestamp.utcnow() - fetched_at > pd.Timedelta(seconds=5)
    return financials, fetched_at, cached


@st.cache_data(show_spinner=False)
def _fetch_news(tickers: Iterable[str]) -> tuple[dict[str, list[dict]], pd.Timestamp]:
    news: dict[str, list[dict]] = {}
    for symbol in tickers:
        ticker = yf.Ticker(symbol)
        news_items = ticker.news or []
        news[symbol] = news_items
    return news, pd.Timestamp.utcnow()


def get_news(tickers: Iterable[str]) -> tuple[dict[str, list[dict]], pd.Timestamp, bool]:
    news, fetched_at = _fetch_news(tickers)
    cached = pd.Timestamp.utcnow() - fetched_at > pd.Timedelta(seconds=5)
    return news, fetched_at, cached
