from __future__ import annotations

from datetime import datetime

import streamlit as st

from backend.ai_generator import generate_recap
from backend.analytics import analyze_race
from backend.fetch_data import get_driver_data, get_race_sessions, load_race_data
from backend.prompt_builder import build_prompt
from backend.visualization import (
    driver_comparison_chart,
    position_change_chart,
    sector_timing_chart,
    speed_vs_lap_chart,
    tire_degradation_chart,
)
from utils.pdf_export import recap_to_pdf_bytes


st.set_page_config(
    page_title="RaceRecapAI",
    page_icon="F1",
    layout="wide",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;600&display=swap');
:root {
  --bg: #0b0c10;
  --panel: #14161a;
  --accent: #e10600;
  --text: #f2f2f2;
  --muted: #8b8f99;
}
html, body, [class*="css"] {
  font-family: 'Rajdhani', sans-serif;
  color: var(--text);
}
.stApp {
  background: radial-gradient(circle at top left, #1a1d22, #0b0c10 50%);
}
section[data-testid="stSidebar"] {
  background-color: #0f1116;
  border-right: 1px solid #20242c;
}
h1, h2, h3 {
  font-family: 'Bebas Neue', sans-serif;
  letter-spacing: 0.5px;
}
.card {
  background: var(--panel);
  border: 1px solid #252a33;
  border-radius: 12px;
  padding: 16px;
}
.badge {
  color: var(--accent);
  font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

st.sidebar.title("RaceRecapAI")
page = st.sidebar.radio("Navigation", ["Race Recap", "About"])

if page == "About":
    st.title("RaceRecapAI")
    st.write(
        "A personalized Formula 1 recap generator powered by FastF1 and IBM watsonx.ai."
    )
    st.stop()

st.title("Personalized Race Recap Dashboard")

current_year = datetime.utcnow().year
season_options = list(range(current_year, 2018, -1))

with st.sidebar:
    season = st.selectbox("Season", season_options)
    races = get_race_sessions(season)
    race_name = st.selectbox("Grand Prix", races if races else ["Select season"])

session = None
if races:
    with st.spinner("Loading race session data..."):
        session = load_race_data(season, race_name)

if session is None:
    st.info("Select a season and Grand Prix to begin.")
    st.stop()

all_drivers = []
for driver_number in session.drivers:
    info = session.get_driver(driver_number)
    all_drivers.append(info["Abbreviation"])

all_drivers = sorted(set(all_drivers))

with st.sidebar:
    driver_abbrev = st.selectbox("Driver", all_drivers)
    style = st.selectbox(
        "Commentary Style", ["Fan Mode", "Technical Analysis", "Casual Summary"]
    )
    generate = st.button("Generate Recap", use_container_width=True)

if not driver_abbrev:
    st.stop()

selected_driver_info = session.get_driver(driver_abbrev)
driver_name = selected_driver_info["FullName"]
team_name = selected_driver_info["TeamName"]

with st.spinner("Analyzing race data..."):
    driver_data = get_driver_data(session, driver_abbrev)
    analytics = analyze_race(session, driver_abbrev)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Start", analytics.get("start_position"))
col2.metric("Finish", analytics.get("end_position"))
col3.metric("Overtakes", analytics.get("overtakes"))
col4.metric("Pit Stops", analytics.get("pit_count"))

st.markdown("---")

left, right = st.columns([2, 1])
with left:
    st.subheader("AI-Powered Recap")
    if generate:
        prompt = build_prompt(
            analytics,
            style,
            driver_name,
            team_name,
            race_name,
            season,
        )
        with st.spinner("Generating recap with watsonx.ai..."):
            recap = generate_recap(prompt)
        st.session_state["recap"] = recap
        if recap.startswith("AI generation failed"):
            st.error(recap)
        else:
            st.success("Recap ready.")

    recap_text = st.session_state.get("recap")
    if recap_text:
        st.write(recap_text)
        pdf_bytes = recap_to_pdf_bytes(
            title=f"{race_name} {season} - {driver_name}",
            body=recap_text,
        )
        st.download_button(
            "Download Recap PDF",
            data=pdf_bytes,
            file_name=f"{race_name}_{season}_{driver_abbrev}.pdf",
            mime="application/pdf",
        )

with right:
    st.subheader("Race Insights")
    average_pace = analytics.get("average_pace")
    avg_pace_str = f"{average_pace:.3f}s" if average_pace else "N/A"
    st.markdown(
        f"<div class='card'>Driver: <span class='badge'>{driver_name}</span><br>"
        f"Team: <span class='badge'>{team_name}</span><br>"
        f"Tire Strategy: {', '.join(analytics.get('tire_strategy', [])) or 'N/A'}<br>"
        f"Avg Pace: {avg_pace_str}"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

st.subheader("Performance Visualizations")

winner_abbrev = None
if session.results is not None and not session.results.empty:
    winner_abbrev = session.results.iloc[0]["Abbreviation"]

fig1 = speed_vs_lap_chart(driver_data.get("telemetry"))
fig2 = driver_comparison_chart(session.laps, driver_abbrev, winner_abbrev)
fig3 = tire_degradation_chart(driver_data.get("laps"))
fig4 = position_change_chart(driver_data.get("laps"))
fig5 = sector_timing_chart(driver_data.get("laps"), session.laps)

row1, row2 = st.columns(2)
row1.plotly_chart(fig1, use_container_width=True)
row2.plotly_chart(fig2, use_container_width=True)

row3, row4 = st.columns(2)
row3.plotly_chart(fig3, use_container_width=True)
row4.plotly_chart(fig4, use_container_width=True)

st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

st.subheader("Fan Q&A")
question = st.text_input("Ask a question about this race or driver")
if st.button("Ask", type="secondary") and question:
    qa_prompt = (
        f"Based on the {race_name} {season} race data for {driver_name}, "
        f"answer the fan question clearly and briefly.\n"
        f"Question: {question}"
    )
    with st.spinner("Generating answer..."):
        answer = generate_recap(qa_prompt)
    st.write(answer)
