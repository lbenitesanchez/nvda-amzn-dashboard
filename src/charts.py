from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLOR_SEQUENCE = px.colors.qualitative.Set2


def build_price_chart(price_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for idx, column in enumerate(price_df.columns):
        fig.add_trace(
            go.Scatter(
                x=price_df.index,
                y=price_df[column],
                mode="lines",
                name=column,
                line=dict(color=COLOR_SEQUENCE[idx % len(COLOR_SEQUENCE)]),
            )
        )
    fig.update_layout(
        title="Price History",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        legend_title_text="Ticker",
    )
    return fig


def build_normalized_chart(cumulative_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for idx, column in enumerate(cumulative_df.columns):
        fig.add_trace(
            go.Scatter(
                x=cumulative_df.index,
                y=cumulative_df[column],
                mode="lines",
                name=column,
                line=dict(color=COLOR_SEQUENCE[idx % len(COLOR_SEQUENCE)]),
            )
        )
    fig.update_layout(
        title="Normalized Performance",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        template="plotly_white",
        legend_title_text="Ticker",
    )
    return fig


def build_bar_chart(df: pd.DataFrame, title: str, yaxis_title: str) -> go.Figure:
    fig = go.Figure()
    for idx, column in enumerate(df.columns):
        fig.add_trace(
            go.Bar(
                x=df.index.astype(str),
                y=df[column],
                name=column,
                marker_color=COLOR_SEQUENCE[idx % len(COLOR_SEQUENCE)],
            )
        )
    fig.update_layout(
        title=title,
        xaxis_title="Period",
        yaxis_title=yaxis_title,
        template="plotly_white",
        legend_title_text="Ticker",
        barmode="group",
    )
    return fig
