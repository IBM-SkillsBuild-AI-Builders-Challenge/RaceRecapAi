from __future__ import annotations

from typing import Dict


STYLE_INSTRUCTIONS = {
    "Fan Mode": "Write with excitement, bold reactions, and fan energy.",
    "Technical Analysis": "Write like a race engineer briefing with technical precision.",
    "Casual Summary": "Write a relaxed recap for casual fans with simple language.",
}


def build_prompt(
    analytics: Dict[str, object],
    style: str,
    driver_name: str,
    team_name: str,
    race_name: str,
    season: int,
) -> str:
    instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["Casual Summary"])
    tire_strategy = ", ".join(analytics.get("tire_strategy", [])) or "unknown"
    avg_pace = analytics.get("average_pace")
    avg_pace_str = f"{avg_pace:.3f}s" if avg_pace else "unknown"
    pit_avg = analytics.get("pit_duration_avg")
    pit_avg_str = f"{pit_avg:.1f}s" if pit_avg else "unknown"

    prompt = (
        f"You are an expert Formula 1 commentator. {instruction}\n\n"
        f"Race: {race_name} {season}\n"
        f"Driver: {driver_name} ({team_name})\n"
        f"Key stats:\n"
        f"- Start position: {analytics.get('start_position')}\n"
        f"- Finish position: {analytics.get('end_position')}\n"
        f"- Position change: {analytics.get('position_change')}\n"
        f"- Overtakes: {analytics.get('overtakes')}\n"
        f"- Average pace: {avg_pace_str}\n"
        f"- Tire strategy: {tire_strategy}\n"
        f"- Pit stops: {analytics.get('pit_count')} (avg {pit_avg_str})\n"
        f"- Safety car laps: {analytics.get('safety_car_laps')}\n\n"
        "Write a personalized race recap in 2-3 paragraphs. "
        "Highlight strategy decisions, pace trends, and decisive moments."
    )
    return prompt
