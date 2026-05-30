from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd


def _to_seconds(series: pd.Series) -> pd.Series:
    return series.dt.total_seconds()


def analyze_race(session, driver_abbrev: str) -> Dict[str, object]:
    """Compute race analytics for the selected driver and race."""
    laps = session.laps
    driver_laps = laps.pick_driver(driver_abbrev)

    fastest_lap_overall = laps.pick_fastest()
    fastest_lap_driver = driver_laps.pick_fastest() if not driver_laps.empty else None

    avg_pace = (
        _to_seconds(driver_laps["LapTime"]).mean() if not driver_laps.empty else None
    )

    def _safe_int(value):
        if value is None or pd.isna(value):
            return None
        return int(value)

    start_pos = _safe_int(driver_laps.iloc[0]["Position"]) if not driver_laps.empty else None
    end_pos = _safe_int(driver_laps.iloc[-1]["Position"]) if not driver_laps.empty else None
    position_change = (
        start_pos - end_pos if start_pos is not None and end_pos is not None else None
    )

    compounds = (
        driver_laps["Compound"].dropna().astype(str).tolist()
        if not driver_laps.empty
        else []
    )
    tire_strategy = []
    for compound in compounds:
        if not tire_strategy or tire_strategy[-1] != compound:
            tire_strategy.append(compound)

    pit_laps = driver_laps[driver_laps["PitInTime"].notna()]
    pit_count = int(pit_laps.shape[0])
    pit_duration = None
    if pit_count > 0:
        pit_duration = (
            (pit_laps["PitOutTime"] - pit_laps["PitInTime"]).dt.total_seconds().mean()
        )

    pos_changes = driver_laps["Position"].diff()
    overtakes = int((pos_changes < 0).sum()) if not driver_laps.empty else 0

    sector_averages = {
        "S1": _to_seconds(driver_laps["Sector1Time"]).mean()
        if not driver_laps.empty
        else None,
        "S2": _to_seconds(driver_laps["Sector2Time"]).mean()
        if not driver_laps.empty
        else None,
        "S3": _to_seconds(driver_laps["Sector3Time"]).mean()
        if not driver_laps.empty
        else None,
    }

    safety_laps = 0
    if not driver_laps.empty and "TrackStatus" in driver_laps.columns:
        safety_laps = int(
            driver_laps["TrackStatus"].astype(str).str.contains("4|5").sum()
        )

    avg_lap_by_driver = (
        laps.groupby("Driver")["LapTime"].apply(lambda x: _to_seconds(x).mean())
    )
    driver_pace_rank = None
    if driver_abbrev in avg_lap_by_driver.index:
        driver_pace_rank = int(avg_lap_by_driver.rank().loc[driver_abbrev])

    return {
        "fastest_lap_overall": fastest_lap_overall,
        "fastest_lap_driver": fastest_lap_driver,
        "average_pace": avg_pace,
        "position_change": position_change,
        "start_position": start_pos,
        "end_position": end_pos,
        "tire_strategy": tire_strategy,
        "pit_count": pit_count,
        "pit_duration_avg": pit_duration,
        "overtakes": overtakes,
        "sector_averages": sector_averages,
        "safety_car_laps": safety_laps,
        "pace_rank": driver_pace_rank,
    }
