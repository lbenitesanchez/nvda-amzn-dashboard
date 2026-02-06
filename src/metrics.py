from __future__ import annotations

import pandas as pd


def compute_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    if price_df.empty:
        return price_df
    return price_df.pct_change().dropna(how="all")


def compute_volatility(returns_df: pd.DataFrame, periods_per_year: int = 252) -> pd.Series:
    if returns_df.empty:
        return pd.Series(dtype=float)
    return returns_df.std() * (periods_per_year**0.5)


def compute_cumulative_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    if price_df.empty:
        return price_df
    return price_df / price_df.iloc[0] - 1


def compute_drawdown(price_df: pd.DataFrame) -> pd.DataFrame:
    if price_df.empty:
        return price_df
    running_max = price_df.cummax()
    return price_df / running_max - 1


def compute_latest_kpis(price_df: pd.DataFrame) -> pd.DataFrame:
    if price_df.empty:
        return pd.DataFrame()
    returns = compute_returns(price_df)
    cumulative = compute_cumulative_returns(price_df)
    drawdown = compute_drawdown(price_df)

    kpis = []
    for column in price_df.columns:
        latest_price = price_df[column].iloc[-1]
        total_return = cumulative[column].iloc[-1]
        max_drawdown = drawdown[column].min()
        latest_return = returns[column].iloc[-1] if not returns.empty else float("nan")
        kpis.append(
            {
                "ticker": column,
                "latest_price": latest_price,
                "total_return": total_return,
                "latest_return": latest_return,
                "max_drawdown": max_drawdown,
            }
        )
    return pd.DataFrame(kpis).set_index("ticker")
