# Luker Intelligence — Premium Quality Dashboard

A dark, interactive Streamlit dashboard for temperature quality monitoring.

## Local run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Upload `app.py`, `requirements.txt`, and the `.streamlit/config.toml` folder to the GitHub repository connected to Streamlit Cloud. Set the main file path to `app.py`.

## Data and security

The initial demo is synthetic and clearly labelled. Actual readings require an authorised Excel/CSV upload. Uploads are processed by the hosting service and should only be used with organisational permission. No sensor readings are embedded in this repository. Missing days are not imputed; daily compliance is calculated from recorded readings. The default target is 18–20°C and can be adjusted in the sidebar.
