from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go


PLOT_TEMPLATE = "plotly_dark"


def speed_vs_lap_chart(telemetry: Optional[pd.DataFrame]) -> go.Figure:
    fig = go.Figure()
    if telemetry is None or telemetry.empty:
        fig.update_layout(
            template=PLOT_TEMPLATE,
            title="Speed vs Distance (no telemetry)",
        )
        return fig

    fig.add_trace(
        go.Scatter(
            x=telemetry["Distance"],
            y=telemetry["Speed"],
            mode="lines",
            name="Speed",
        )
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title="Speed vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
    )
    return fig


def driver_comparison_chart(
    laps: pd.DataFrame, driver_abbrev: str, comparison_abbrev: Optional[str]
) -> go.Figure:
    fig = go.Figure()
    driver_laps = laps.pick_driver(driver_abbrev)
    if driver_laps.empty:
        fig.update_layout(template=PLOT_TEMPLATE, title="Driver Lap Time Comparison")
        return fig
    fig.add_trace(
        go.Scatter(
            x=driver_laps["LapNumber"],
            y=driver_laps["LapTime"].dt.total_seconds(),
            mode="lines+markers",
            name=driver_abbrev,
        )
    )
    if comparison_abbrev:
        comp_laps = laps.pick_driver(comparison_abbrev)
        fig.add_trace(
            go.Scatter(
                x=comp_laps["LapNumber"],
                y=comp_laps["LapTime"].dt.total_seconds(),
                mode="lines+markers",
                name=comparison_abbrev,
            )
        )

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title="Driver Lap Time Comparison",
        xaxis_title="Lap",
        yaxis_title="Lap Time (s)",
    )
    return fig


def tire_degradation_chart(driver_laps: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if driver_laps.empty:
        fig.update_layout(template=PLOT_TEMPLATE, title="Tire Degradation")
        return fig

    for compound in driver_laps["Compound"].dropna().unique():
        compound_laps = driver_laps[driver_laps["Compound"] == compound]
        fig.add_trace(
            go.Scatter(
                x=compound_laps["LapNumber"],
                y=compound_laps["LapTime"].dt.total_seconds(),
                mode="lines+markers",
                name=f"{compound}",
            )
        )

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title="Tire Degradation (Lap Time)",
        xaxis_title="Lap",
        yaxis_title="Lap Time (s)",
    )
    return fig


def position_change_chart(driver_laps: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if driver_laps.empty:
        fig.update_layout(template=PLOT_TEMPLATE, title="Position Change")
        return fig

    fig.add_trace(
        go.Scatter(
            x=driver_laps["LapNumber"],
            y=driver_laps["Position"],
            mode="lines+markers",
            name="Position",
        )
    )
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title="Position Change",
        xaxis_title="Lap",
        yaxis_title="Position",
        yaxis_autorange="reversed",
    )
    return fig


def sector_timing_chart(driver_laps: pd.DataFrame, all_laps: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if driver_laps.empty:
        fig.update_layout(template=PLOT_TEMPLATE, title="Sector Timing")
        return fig

    driver_avg = [
        driver_laps["Sector1Time"].dt.total_seconds().mean(),
        driver_laps["Sector2Time"].dt.total_seconds().mean(),
        driver_laps["Sector3Time"].dt.total_seconds().mean(),
    ]
    field_avg = [
        all_laps["Sector1Time"].dt.total_seconds().mean(),
        all_laps["Sector2Time"].dt.total_seconds().mean(),
        all_laps["Sector3Time"].dt.total_seconds().mean(),
    ]

    fig.add_trace(go.Bar(x=["S1", "S2", "S3"], y=driver_avg, name="Driver"))
    fig.add_trace(go.Bar(x=["S1", "S2", "S3"], y=field_avg, name="Field"))

    fig.update_layout(
        template=PLOT_TEMPLATE,
        title="Sector Timing Comparison",
        xaxis_title="Sector",
        yaxis_title="Average Time (s)",
        barmode="group",
    )
    return fig
