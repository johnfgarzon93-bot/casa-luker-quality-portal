import io
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='Quality Control | Temperature', page_icon='🌡️', layout='wide')
st.markdown('''<style>
.stApp {background:#f5f8fd;color:#12213a} .block-container{padding-top:1.6rem;max-width:1350px}
[data-testid="stMetric"]{background:white;border:1px solid #e0e9f4;border-radius:13px;padding:17px}
h1,h2,h3{color:#123b70} .stButton>button{background:#164b89;color:white;border-radius:9px}
</style>''', unsafe_allow_html=True)
st.caption('QUALITY CONTROL  /  TEMPERATURE MONITORING')
st.title('Temperature Performance Dashboard')
st.write('Interactive temperature monitoring · Target range **18–20 °C**')
st.info('Public prototype: upload an authorised file to analyse it in your current session. Do not upload confidential operational data to a public service without company approval. Uploaded data is not saved by this app.')

with st.sidebar:
    st.header('Data source')
    uploaded = st.file_uploader('Upload temperature Excel', type=['xlsx','csv'])
    st.caption('Expected columns: Date/Time and SENSOR 1 (°C).')
    demo = st.toggle('Show synthetic demo', value=True, disabled=uploaded is not None)

@st.cache_data(show_spinner=False)
def load_data(contents, name):
    raw = pd.read_csv(io.BytesIO(contents)) if name.lower().endswith('.csv') else pd.read_excel(io.BytesIO(contents))
    if raw.shape[1] < 2:
        raise ValueError('The file needs at least two columns.')
    cols = list(raw.columns)
    date_col = next((c for c in cols if 'date' in str(c).lower() or 'time' in str(c).lower()), cols[0])
    temp_col = next((c for c in cols if 'sensor' in str(c).lower() or 'temp' in str(c).lower() or '°c' in str(c).lower()), cols[1])
    df = raw[[date_col,temp_col]].copy()
    df.columns = ['timestamp','temperature']
    if pd.api.types.is_numeric_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='D', origin='1899-12-30', errors='coerce')
    else:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', dayfirst=True)
    df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
    return df.dropna().sort_values('timestamp')

if uploaded is not None:
    try:
        df = load_data(uploaded.getvalue(), uploaded.name)
    except Exception as e:
        st.error(f'Could not read file: {e}')
        st.stop()
    st.success(f'Loaded {len(df):,} measured readings from the uploaded file.')
elif demo:
    import math
    dates = pd.date_range('2026-10-01', periods=33, freq='D')
    df = pd.DataFrame({'timestamp': dates, 'temperature': [round(17.75+0.45*math.sin(i*0.72)+0.17*math.cos(i*1.9),2) for i in range(len(dates))]})
    st.warning('SYNTHETIC DEMO DATA — not actual Dincer measurements. Upload an authorised Excel to see real statistics.')
else:
    st.info('Upload an Excel file to begin, or enable the synthetic demo.')
    st.stop()

if df.empty:
    st.error('No valid temperature readings found.')
    st.stop()

df['date'] = df['timestamp'].dt.date
all_dates = sorted(df['date'].unique())
with st.sidebar:
    st.header('Filters')
    selected = st.date_input('Date range', value=(all_dates[0], all_dates[-1]), min_value=all_dates[0], max_value=all_dates[-1])
    if isinstance(selected, tuple) and len(selected)==2:
        df = df[(df['date']>=selected[0]) & (df['date']<=selected[1])]
if df.empty:
    st.warning('No readings in selected period.')
    st.stop()

in_range = df['temperature'].between(18,20,inclusive='both')
below = df['temperature']<18
above = df['temperature']>20
c1,c2,c3,c4,c5=st.columns(5)
c1.metric('Average', f"{df['temperature'].mean():.2f} °C")
c2.metric('Minimum', f"{df['temperature'].min():.1f} °C")
c3.metric('Maximum', f"{df['temperature'].max():.1f} °C")
c4.metric('Within target', f'{in_range.mean()*100:.1f}%')
c5.metric('Below target', f'{below.mean()*100:.1f}%')
st.caption(f"{len(df):,} readings · {df['timestamp'].min():%d %b %Y %H:%M} to {df['timestamp'].max():%d %b %Y %H:%M} · {df['date'].nunique()} days with readings")

daily = df.groupby('date').agg(readings=('temperature','size'),avg=('temperature','mean'),min=('temperature','min'),max=('temperature','max')).reset_index()
daily['below_pct'] = df.assign(below=below).groupby('date')['below'].mean().to_numpy()*100
daily['within_pct'] = df.assign(within=in_range).groupby('date')['within'].mean().to_numpy()*100
left,right=st.columns([2,1])
with left:
    st.subheader('Daily temperature trend')
    fig=go.Figure()
    fig.add_hrect(y0=18,y1=20,fillcolor='rgba(42,145,115,.12)',line_width=0,annotation_text='Target 18–20 °C',annotation_position='top left')
    fig.add_trace(go.Scatter(x=daily['date'],y=daily['avg'],name='Daily average',mode='lines+markers',line=dict(color='#e2aa20',width=3)))
    fig.add_trace(go.Scatter(x=daily['date'],y=daily['min'],name='Daily minimum',mode='lines',line=dict(color='#73a4d7',dash='dot')))
    fig.add_trace(go.Scatter(x=daily['date'],y=daily['max'],name='Daily maximum',mode='lines',line=dict(color='#164b89',dash='dot')))
    fig.update_layout(height=390,template='plotly_white',margin=dict(l=10,r=10,t=20,b=10),yaxis_title='°C',legend=dict(orientation='h',y=-.25))
    st.plotly_chart(fig,use_container_width=True)
with right:
    st.subheader('Compliance breakdown')
    donut=px.pie(values=[int(below.sum()),int(in_range.sum()),int(above.sum())],names=['Below 18°C','18–20°C','Above 20°C'],hole=.64,color_discrete_sequence=['#e2aa20','#217b67','#ba4355'])
    donut.update_layout(height=390,margin=dict(l=0,r=0,t=10,b=10),legend=dict(orientation='h',y=-.1))
    st.plotly_chart(donut,use_container_width=True)

st.subheader('Daily performance')
st.dataframe(daily.rename(columns={'date':'Date','readings':'Readings','avg':'Average °C','min':'Min °C','max':'Max °C','below_pct':'Below target %','within_pct':'Within target %'}).style.format({'Average °C':'{:.2f}','Min °C':'{:.1f}','Max °C':'{:.1f}','Below target %':'{:.1f}','Within target %':'{:.1f}'}),use_container_width=True,hide_index=True)
st.download_button('Download daily statistics (CSV)',daily.to_csv(index=False).encode('utf-8'),'temperature_daily_statistics.csv','text/csv')
st.caption('Note: A day with no measurements is not treated as compliant. Source differences should be resolved before issuing official quality conclusions.')
