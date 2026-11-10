import io
import math
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Luker Intelligence | Quality", page_icon="✦", layout="wide", initial_sidebar_state="expanded")
BG="#081422"; PANEL="#102238"; TEXT="#EAF4FF"; MUTED="#91AAC1"; TEAL="#55DAC9"; GOLD="#F2BD67"; RED="#FB7988"; BLUE="#78A9F7"
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif!important}
.stApp{background:radial-gradient(ellipse at 78% 0%,#153350 0%,#081422 48%,#07111f 100%);color:#EAF4FF}
[data-testid="stSidebar"]{background:#0C1B2E;border-right:1px solid #243951}
.block-container{max-width:1540px;padding-top:2.2rem;padding-bottom:4rem}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:#F1F8FF!important;letter-spacing:-.035em}
h1{font-weight:800!important;font-size:2.45rem!important}h3{font-size:1.18rem!important}
p,span,label{color:inherit} [data-testid="stCaptionContainer"]{color:#91AAC1!important}
[data-testid="stMetric"]{background:linear-gradient(140deg,#152B43,#102238);border:1px solid #29445D;border-radius:18px;padding:19px 21px;box-shadow:0 14px 35px #02091440}
[data-testid="stMetricLabel"]{color:#A3B8CB!important;font-weight:600}[data-testid="stMetricValue"]{color:#F5FBFF!important;font-family:'Manrope',sans-serif;font-weight:800}
[data-testid="stMetricDelta"]{color:#55DAC9!important}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:#2B455D!important}
.stButton>button,.stDownloadButton>button{border-radius:12px!important;background:#183C55!important;color:#DDFCF5!important;border:1px solid #397185!important;font-weight:700}
.stButton>button:hover,.stDownloadButton>button:hover{background:#236177!important;border-color:#55DAC9!important}
[data-testid="stFileUploader"]{border-radius:14px} [data-testid="stAlert"]{border-radius:13px}
[data-testid="stDataFrame"]{border:1px solid #29445D;border-radius:14px;overflow:hidden}
hr{border-color:#29445D!important}
.hero{padding:28px 32px;border:1px solid #2D4C65;border-radius:24px;background:linear-gradient(110deg,#173B53,#10243B 65%,#112A41);margin-bottom:25px;box-shadow:0 20px 55px #00000025}
.eyebrow{font-size:11px;letter-spacing:.22em;font-weight:800;color:#55DAC9}.hero-title{font-family:Manrope,sans-serif;font-size:35px;letter-spacing:-.05em;font-weight:800;color:#fff;margin:8px 0}.hero-sub{color:#AFC4D5;font-size:14px}.pill{display:inline-block;padding:7px 12px;background:#23546A;border:1px solid #3C8290;border-radius:100px;color:#9FF5E9;font-size:11px;font-weight:700;margin-top:17px}
.section-label{font-size:11px;letter-spacing:.15em;font-weight:800;color:#78A9F7;margin:25px 0 8px}
</style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(contents, name):
    raw = pd.read_csv(io.BytesIO(contents)) if name.lower().endswith('.csv') else pd.read_excel(io.BytesIO(contents))
    if raw.shape[1]<2: raise ValueError('At least two columns are required.')
    cols=list(raw.columns)
    dc=next((c for c in cols if 'date' in str(c).lower() or 'time' in str(c).lower()),cols[0])
    tc=next((c for c in cols if 'sensor' in str(c).lower() or 'temp' in str(c).lower() or '°c' in str(c).lower()),cols[1])
    if dc==tc: raise ValueError('Date and temperature columns must be different.')
    df=raw[[dc,tc]].copy();df.columns=['timestamp','temperature']
    if pd.api.types.is_numeric_dtype(df.timestamp): df['timestamp']=pd.to_datetime(df.timestamp,unit='D',origin='1899-12-30',errors='coerce')
    else: df['timestamp']=pd.to_datetime(df.timestamp,errors='coerce',dayfirst=True)
    df['temperature']=pd.to_numeric(df.temperature,errors='coerce')
    return df.dropna().sort_values('timestamp').reset_index(drop=True)

def chart_style(fig,height=400):
    fig.update_layout(height=height,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color=MUTED,family='DM Sans'),margin=dict(l=12,r=16,t=24,b=32),hovermode='x unified',legend=dict(orientation='h',y=-.19,x=0,font=dict(size=11)),xaxis=dict(showgrid=False,zeroline=False),yaxis=dict(gridcolor='#294056',zeroline=False),uirevision='quality')
    return fig

with st.sidebar:
    st.markdown('### ✦ LUKER INTELLIGENCE')
    st.caption('QUALITY OPERATIONS · ANALYTICS')
    st.divider()
    page=st.radio('WORKSPACE',['◈  Executive overview','⌁  Temperature intelligence','▦  Daily performance','≡  Data explorer'],label_visibility='collapsed')
    st.divider()
    st.markdown('#### DATA SOURCE')
    uploaded=st.file_uploader('Upload authorised Excel / CSV',type=['xlsx','csv'])
    demo=st.toggle('Explore sample data',value=True,disabled=uploaded is not None)
    st.caption('Expected: date/time and temperature sensor columns.')
    st.divider()
    st.caption('Privacy: only upload company records with authorisation. Public hosting processes uploaded files.')

if uploaded is not None:
    try: df=load_data(uploaded.getvalue(),uploaded.name)
    except Exception as e: st.error(f'Unable to parse file: {e}');st.stop()
    source='UPLOADED MEASUREMENTS'; is_demo=False
elif demo:
    dates=pd.date_range('2026-10-01',periods=33,freq='D')
    df=pd.DataFrame({'timestamp':dates,'temperature':[round(17.75+.45*math.sin(i*.72)+.17*math.cos(i*1.9),2) for i in range(len(dates))]})
    source='SYNTHETIC SAMPLE · NOT REAL MEASUREMENTS';is_demo=True
else:
    st.info('Upload an authorised file or enable sample data to explore the dashboard.');st.stop()
if df.empty: st.error('No valid readings found.');st.stop()

df['date']=df.timestamp.dt.date
first,last=df.date.min(),df.date.max()
with st.sidebar:
    st.markdown('#### FILTERS')
    chosen=st.date_input('Date range',value=(first,last),min_value=first,max_value=last)
    low,high=st.slider('Target temperature (°C)',min_value=0.,max_value=35.,value=(18.,20.),step=.5)
if isinstance(chosen,(tuple,list)) and len(chosen)==2: df=df.loc[df.date.between(chosen[0],chosen[1])].copy()
if df.empty: st.warning('No readings for the selected dates.');st.stop()

inside=df.temperature.between(low,high);below=df.temperature<low;above=df.temperature>high
df['status']='Within target';df.loc[below,'status']='Below target';df.loc[above,'status']='Above target'
daily=df.groupby('date',as_index=False).agg(readings=('temperature','size'),avg=('temperature','mean'),min=('temperature','min'),max=('temperature','max'))
daily['within_pct']=df.assign(ok=inside).groupby('date')['ok'].mean().to_numpy()*100
daily['below_pct']=df.assign(bad=below).groupby('date')['bad'].mean().to_numpy()*100
st.markdown(f'''<div class="hero"><div class="eyebrow">QUALITY OPERATIONS / ANALYTICS SUITE</div><div class="hero-title">{page.split('  ',1)[-1]}</div><div class="hero-sub">Operational temperature intelligence · Interactive monitoring and performance analytics</div><div class="pill">{source}</div></div>''',unsafe_allow_html=True)
if is_demo: st.warning('Sample mode: every measurement shown is synthetic. Upload an authorised source file to analyse actual readings.')
else: st.success(f'{len(df):,} valid readings loaded from {uploaded.name}.')

st.markdown('<div class="section-label">PERFORMANCE SNAPSHOT</div>',unsafe_allow_html=True)
cols=st.columns(5)
for c,(label,value) in zip(cols,[('Average',f'{df.temperature.mean():.2f} °C'),('Minimum',f'{df.temperature.min():.2f} °C'),('Maximum',f'{df.temperature.max():.2f} °C'),('In target',f'{inside.mean()*100:.1f}%'),('Out of target',f'{(~inside).mean()*100:.1f}%')]): c.metric(label,value)
st.caption(f'{len(df):,} readings  ·  {df.timestamp.min():%d %b %Y %H:%M} — {df.timestamp.max():%d %b %Y %H:%M}  ·  {df.date.nunique()} observed days  ·  Target {low:g}–{high:g} °C')

if 'overview' in page or 'Temperature' in page:
    st.markdown('<div class="section-label">MONITORING & DISTRIBUTION</div>',unsafe_allow_html=True)
    left,right=st.columns([1.9,1],gap='large')
    with left:
        st.subheader('Temperature evolution')
        view=st.segmented_control('Resolution',['Daily averages','Individual readings'],default='Daily averages',label_visibility='collapsed')
        fig=go.Figure();fig.add_hrect(y0=low,y1=high,fillcolor='rgba(85,218,201,.11)',line_width=0)
        fig.add_hline(y=low,line_dash='dot',line_color='#5B9E9D');fig.add_hline(y=high,line_dash='dot',line_color='#5B9E9D')
        if view=='Daily averages':
            fig.add_trace(go.Scatter(x=daily.date,y=daily.avg,name='Daily average',mode='lines+markers',line=dict(color=GOLD,width=3),marker=dict(size=6)))
            fig.add_trace(go.Scatter(x=daily.date,y=daily['min'],name='Minimum',mode='lines',line=dict(color=BLUE,width=1.6,dash='dot')))
            fig.add_trace(go.Scatter(x=daily.date,y=daily['max'],name='Maximum',mode='lines',line=dict(color=TEAL,width=1.6,dash='dot')))
        else:
            fig.add_trace(go.Scatter(x=df.timestamp,y=df.temperature,name='Sensor readings',mode='lines+markers',line=dict(color=GOLD,width=2),marker=dict(size=4)))
        chart_style(fig,430);fig.update_yaxes(title_text='Temperature °C')
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.subheader('Compliance profile')
        vals=[int(below.sum()),int(inside.sum()),int(above.sum())]
        donut=go.Figure(go.Pie(labels=[f'Below {low:g}°C','Within target',f'Above {high:g}°C'],values=vals,hole=.72,marker=dict(colors=[GOLD,TEAL,RED]),sort=False,textinfo='percent',hovertemplate='%{label}: %{value} readings<extra></extra>'))
        donut.update_layout(annotations=[dict(text=f'<b>{inside.mean()*100:.1f}%</b><br><span style="font-size:12px">IN TARGET</span>',showarrow=False,font=dict(color=TEXT,size=23))],showlegend=True)
        chart_style(donut,430);st.plotly_chart(donut,use_container_width=True)
    if 'Temperature' in page:
        st.subheader('Distribution of recorded temperatures')
        hist=go.Figure(go.Histogram(x=df.temperature,marker_color=BLUE,opacity=.88,nbinsx=25))
        hist.add_vrect(x0=low,x1=high,fillcolor='rgba(85,218,201,.12)',line_width=0)
        chart_style(hist,340);hist.update_xaxes(title_text='Temperature °C');hist.update_yaxes(title_text='Readings')
        st.plotly_chart(hist,use_container_width=True)

if 'overview' in page or 'Daily' in page:
    st.markdown('<div class="section-label">DAILY PERFORMANCE</div>',unsafe_allow_html=True)
    st.subheader('Compliance by day')
    fig=go.Figure(go.Bar(x=daily.date,y=daily.within_pct,marker_color=[TEAL if v>=90 else GOLD if v>=50 else RED for v in daily.within_pct],name='In target'))
    chart_style(fig,330);fig.update_yaxes(title_text='In target %',range=[0,105]);st.plotly_chart(fig,use_container_width=True)
    display=daily.rename(columns={'date':'Date','readings':'Readings','avg':'Average °C','min':'Minimum °C','max':'Maximum °C','within_pct':'In target %','below_pct':'Below target %'})
    st.dataframe(display.style.format({'Average °C':'{:.2f}','Minimum °C':'{:.2f}','Maximum °C':'{:.2f}','In target %':'{:.1f}','Below target %':'{:.1f}'}),hide_index=True,use_container_width=True)

if 'Data explorer' in page:
    st.markdown('<div class="section-label">DATA EXPLORER</div>',unsafe_allow_html=True)
    st.subheader('Individual measurements')
    status=st.multiselect('Filter by status',['Within target','Below target','Above target'],default=['Within target','Below target','Above target'])
    records=df.loc[df.status.isin(status),['timestamp','temperature','status']].rename(columns={'timestamp':'Timestamp','temperature':'Temperature °C','status':'Status'})
    st.dataframe(records,use_container_width=True,hide_index=True,height=520)
    st.download_button('↓ Download filtered measurements',records.to_csv(index=False).encode(),'temperature_measurements.csv','text/csv')

st.divider()
a,b=st.columns([2,1]);a.caption('Quality intelligence · Missing days are never imputed. Percentages are based on recorded readings, not elapsed time.')
b.download_button('↓ Export daily statistics',daily.to_csv(index=False).encode(),'temperature_daily_statistics.csv','text/csv',use_container_width=True)
