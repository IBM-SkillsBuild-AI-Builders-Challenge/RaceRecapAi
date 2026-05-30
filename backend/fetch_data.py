from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fastf1
import pandas as pd


CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "fastf1_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


@lru_cache(maxsize=64)
def get_race_sessions(season: int) -> List[str]:
    """Return a list of race names for a given season."""
    schedule = fastf1.get_event_schedule(season, include_testing=False)
    if "Session5" in schedule.columns:
        schedule = schedule[schedule["Session5"] == "Race"]
    races = schedule["EventName"].dropna().tolist()
    return races


@lru_cache(maxsize=64)
def load_race_data(season: int, race_name: str) -> fastf1.core.Session:
    """Load and return the race session data for a specific event."""
    session = fastf1.get_session(season, race_name, "R")
    session.load(telemetry=True, laps=True, weather=False)
    return session


def get_driver_data(
    session: fastf1.core.Session, driver_abbrev: str
) -> Dict[str, Optional[pd.DataFrame]]:
    """Extract driver-specific laps, telemetry, and pit stop data."""
    laps = session.laps.pick_driver(driver_abbrev)
    telemetry = None
    if not laps.empty:
        fastest = laps.pick_fastest()
        if fastest is not None:
            telemetry = fastest.get_telemetry()

    pit_laps = laps[laps["PitInTime"].notna()] if not laps.empty else pd.DataFrame()

    return {
        "laps": laps,
        "telemetry": telemetry,
        "pit_laps": pit_laps,
    }
