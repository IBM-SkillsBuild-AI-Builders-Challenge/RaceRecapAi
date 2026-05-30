# RaceRecapAI

AI-powered Formula 1 personalized race recap generator built with Streamlit, FastF1, and IBM watsonx.ai.

## Features
- Season, race, and driver selection
- FastF1 data loading with cache
- Race analytics and insights
- Interactive Plotly charts
- AI-generated personalized recaps (IBM Granite)
- Fan Q&A
- Download recap as PDF

## Project Structure
```
RaceRecapAI/
├── app.py
├── requirements.txt
├── .env
├── backend/
│   ├── fetch_data.py
│   ├── analytics.py
│   ├── visualization.py
│   ├── prompt_builder.py
│   └── ai_generator.py
├── assets/
├── data/
├── utils/
│   └── pdf_export.py
└── README.md
```

## Setup
1. Create a virtual environment (Python 3.10+).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure IBM watsonx.ai credentials in `.env`:
   ```
   WATSONX_API_KEY=your_key_here
   WATSONX_URL=https://us-south.ml.cloud.ibm.com
   WATSONX_PROJECT_ID=your_project_id_here
   WATSONX_MODEL_ID=ibm/granite-13b-chat-v2
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Notes
- FastF1 cache is stored under `data/fastf1_cache`.
- The first run for a race can take time depending on telemetry size.

## Screenshot Placeholders
Add screenshots to `assets/` with names like:
- `dashboard.png`
- `charts.png`
- `recap.png`

## License
For educational and demo purposes.
