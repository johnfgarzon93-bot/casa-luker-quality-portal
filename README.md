# DİNÇER | Temperature Intelligence

A strategic Streamlit dashboard with a premium dark UI, smooth interactive Plotly temperature charts, and London outdoor temperature and apparent temperature from the Open-Meteo Historical Weather API.

## Important data integrity notes
- The chart image supplied by the user includes two segments: blue through 23 October 2026 and amber from 24 October through 10 November 2026.
- The file `data/chart_reconstruction.csv` contains **approximate daily values digitised visually from the screenshot**. It is NOT an original sensor export, and MUST NOT be presented as exact measurements.
- The screenshot's reported KPIs are preserved as *reported figures*: 17.30°C mean, 15.8°C minimum, and 80.5% below 18°C. These figures should not be recomputed from the approximate chart points.
- The weather series are fetched from Open-Meteo's archive endpoint at runtime, using central London coordinates (51.5074, -0.1278). Daily means are calculated from hourly `temperature_2m` and `apparent_temperature` in Europe/London time. These are meteorological gridded estimates, not onsite thermometer readings. The API can be unavailable or recent dates can be incomplete.
- No synthetic demo is shown. Missing data remains missing. Smoothing is purely visual.

## Deploy
1. Upload all files and folders (including hidden `.streamlit/config.toml`) to your GitHub repo.
2. In Streamlit Community Cloud, choose `app.py` as the main file and deploy/reboot.
3. Open the **Data controls and source settings** panel to upload the actual sensor export. It replaces the chart reconstruction for that session.
4. If using real company operational records, obtain permission before uploading to a third-party public cloud application. Do not commit sensitive exports to a public repository.

## Local run
```
pip install -r requirements.txt
streamlit run app.py
```

Weather data: https://open-meteo.com/en/docs/historical-weather-api
