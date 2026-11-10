# Temperature Performance Dashboard

A Streamlit web dashboard for authorised temperature readings.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publish publicly

1. Create a GitHub repository and upload `app.py`, `requirements.txt` and `README.md`.
2. Visit https://share.streamlit.io, sign in with GitHub, choose the repository and `app.py`, then deploy.
3. Share the generated `*.streamlit.app` URL.

**Data security:** Do not commit company temperature exports or confidential records to a public GitHub repository. The app starts with clearly labelled synthetic demonstration data; real data can be uploaded for session analysis only with company authorisation. Streamlit's cloud infrastructure still processes uploads, so review your organisation's security requirements before using it with company data.

**Data validity:** The application reports the values in the uploaded file; it does not validate that sensor records are authentic or reconcile conflicting historical exports. Missing days are not imputed.
