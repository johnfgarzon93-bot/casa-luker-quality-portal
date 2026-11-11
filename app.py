import io
import base64
import zlib
from datetime import date
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title='Casa Luker | Quality Intelligence',page_icon='◈',layout='wide',initial_sidebar_state='collapsed')
NAVY='#091525'; PANEL='#13273d'; AQUA='#59dfd0'; GOLD='#f1b94e'; SKY='#71aaf2'; MUTED='#9db2c8'
st.markdown('''<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"]{display:none!important}
#MainMenu,footer,header[data-testid="stHeader"]{visibility:hidden;height:0}
.stApp{background:radial-gradient(ellipse at 85% -15%,#163855 0%,#091525 48%);color:#edf5fc}
.block-container{max-width:1480px;padding:1.15rem 2rem 3rem}
html,body,[class*="css"]{font-family:Inter,system-ui,sans-serif}
h1,h2,h3{letter-spacing:-.035em!important;color:#f0f7ff!important}
h1{font-size:clamp(1.7rem,3vw,2.55rem)!important;margin:0!important}
h3{font-size:1.05rem!important}
[data-testid="stMetric"]{background:linear-gradient(150deg,#1a324c,#11243a);border:1px solid #2b455d;border-radius:17px;padding:18px;min-width:0}
[data-testid="stMetricLabel"]{color:#a8c1d3!important;font-size:.78rem!important;letter-spacing:.025em}
[data-testid="stMetricValue"]{font-size:clamp(1.35rem,2.4vw,2rem)!important;color:#fff!important;overflow-wrap:anywhere}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#28445e!important;border-radius:16px!important}
.stButton>button,.stDownloadButton>button{border-radius:12px;background:#183750;color:#e8f8ff;border:1px solid #38566c}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#59dfd0;color:#59dfd0}
[data-testid="stAlert"]{border-radius:12px}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
@media(max-width:750px){.block-container{padding:1rem .85rem 2rem}[data-testid="stMetric"]{padding:12px}[data-testid="stMetricValue"]{font-size:1.35rem!important}}
</style>''',unsafe_allow_html=True)

st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;border-bottom:1px solid #28435a;padding:4px 0 18px"><div style="font-weight:800;letter-spacing:.11em;color:#f0f8ff;font-size:1rem">🇨🇴 CASA LUKER <span style="color:#59dfd0">INTELLIGENCE</span> 🇬🇧</div><div style="font-size:.76rem;color:#a2b8cc">COLOMBIA × UNITED KINGDOM · QUALITY OPERATIONS</div></div>',unsafe_allow_html=True)
page=st.radio('Navigation',['Overview','Temperature trends','London weather','Data & methodology'],horizontal=True,label_visibility='collapsed')

@st.cache_data

def read_reconstruction():
    # Self-contained fallback: deployed app works even if GitHub upload omits data/.
    file_path = Path(__file__).resolve().parent / 'data' / 'chart_reconstruction.csv'
    if file_path.is_file():
        return pd.read_csv(file_path, parse_dates=['date'])
    embedded = 'eNrF10FOwzAQBdA9EnfwAVLkcRInESt27OAGlUmGYimtg+2Icntip0hcAP9lpMavdWe+PZOJXEU+L+xNXD0fxyqwtxyq4FY/8vFzNbON3/d3Sip9IHmQVFH3oKtnG6LzdjSzCHwJzovbi0/L4t3VnreVhWcz2ctJTPZkow08iXfvziKsyzLb7Wn8MD6K7bMnfhQXF4U3X7/L8XVxPv6BVYJrAFyj4CbBCgC3CW4BsE5wA4C7BBMA7ivSkHYaEtyVh0mmrR4A8JZcPaKPSSUY0E6Uk6sHwA3okKAW1MekUzshqrpD9XFOLkRV5+QCHBJKgrZa5TsXAs7JBbiBqBp0SKhmj8xXF+L2LcTLGN0b/z/b7htdmtV7YZVmb5lVmu3Tr5XF2WGfHwqztYT8tzUBKpnyWJruWKXZHJCyOHuLx9IsIhwpj6P9duCXZjVmkztMSfWYvh32oawwuw+hxSr5BxzPvKY='
    csv_bytes = zlib.decompress(base64.b64decode(embedded))
    return pd.read_csv(io.BytesIO(csv_bytes), parse_dates=['date'])

@st.cache_data(ttl=21600,show_spinner=False)
def weather_data(lat,lon,first,last):
 url='https://archive-api.open-meteo.com/v1/archive'
 params={'latitude':lat,'longitude':lon,'start_date':str(first),'end_date':str(last),'hourly':'temperature_2m,apparent_temperature','timezone':'Europe/London'}
 r=requests.get(url,params=params,timeout=25);r.raise_for_status();j=r.json()
 h=j.get('hourly',{})
 if not h.get('time'):raise ValueError('No hourly weather records returned')
 d=pd.DataFrame({'timestamp':pd.to_datetime(h['time']),'outside_c':h['temperature_2m'],'feels_like_c':h['apparent_temperature']})
 d['date']=d['timestamp'].dt.normalize()
 return d.groupby('date',as_index=False)[['outside_c','feels_like_c']].mean()

base=read_reconstruction()
with st.expander('⚙ Data controls and source settings',expanded=False):
 a,b,c=st.columns([2,1,1]);uploaded=a.file_uploader('Replace chart reconstruction with a sensor export (CSV / XLSX)',type=['csv','xlsx']);start=b.date_input('From',value=date(2026,10,1),min_value=date(2026,10,1),max_value=date(2026,11,10));end=c.date_input('To',value=date(2026,11,10),min_value=date(2026,10,1),max_value=date(2026,11,10))
 st.caption('Weather reference: central London (51.5074, -0.1278). The chiller location may differ; weather is context, not an indoor measurement.')

source='chart'
if uploaded:
 try:
  d=pd.read_csv(io.BytesIO(uploaded.getvalue())) if uploaded.name.lower().endswith('.csv') else pd.read_excel(io.BytesIO(uploaded.getvalue()))
  cols=list(d.columns);dc=next((x for x in cols if 'date' in str(x).lower() or 'time' in str(x).lower()),cols[0]);tc=next((x for x in cols if 'temp' in str(x).lower() or 'sensor' in str(x).lower() or '°c' in str(x).lower()),cols[1])
  d=d[[dc,tc]].rename(columns={dc:'date',tc:'temperature_c'});d['date']=pd.to_datetime(d['date'],errors='coerce',dayfirst=True).dt.normalize();d['temperature_c']=pd.to_numeric(d['temperature_c'],errors='coerce');d=d.dropna()
  if d.empty:raise ValueError('No valid sensor rows')
  d=d.groupby('date',as_index=False)['temperature_c'].mean();d['series']='Uploaded sensor data';d['source_quality']='Uploaded file; source authenticity not independently verified';base=d;source='uploaded'
 except Exception as exc:st.error(f'File could not be parsed: {exc}');st.stop()
if start>end:st.warning('Start date must be before end date.');st.stop()
df=base[(base.date.dt.date>=start)&(base.date.dt.date<=end)].copy()
if df.empty:st.warning('No indoor readings for the selected period.');st.stop()
try:
 weather=weather_data(51.5074,-0.1278,start,end);weather_error=None
except Exception as exc:
 weather=pd.DataFrame(columns=['date','outside_c','feels_like_c']);weather_error=str(exc)
merged=df.merge(weather,on='date',how='left')

st.markdown('<div style="margin:18px 0 5px;color:#59dfd0;font-size:.73rem;font-weight:700;letter-spacing:.14em">OPERATIONS / PERFORMANCE</div>',unsafe_allow_html=True)
st.title({'Overview':'Temperature performance overview','Temperature trends':'Chiller temperature trends','London weather':'London weather intelligence','Data & methodology':'Data management & methodology'}[page])
st.caption(f'{start:%d %B} – {end:%d %B %Y}  ·  Target 18.0–20.0 °C  ·  {"Uploaded sensor file" if source=="uploaded" else "Chart-derived reconstruction"}')
if source=='chart':
 st.info('The indoor daily points are approximate values read from the supplied chart, not raw sensor readings. Original report KPIs: mean 17.30°C, minimum 15.8°C, below 18°C 80.5% (1 Oct–10 Nov). These report KPIs are not recomputed from the reconstruction.')
if weather_error:st.warning('London weather is temporarily unavailable from Open-Meteo. Indoor data remains visible; no weather values have been substituted.')

if page in ('Overview','Temperature trends'):
 if source=='chart' and start==date(2026,10,1) and end==date(2026,11,10):
  cards=[('Reported sensor mean','17.30°C'),('Reported minimum','15.8°C'),('Reported below target','80.5%'),('Chart period','41 days')]
 else:
  cards=[('Period mean*',f'{df.temperature_c.mean():.2f}°C'),('Period minimum*',f'{df.temperature_c.min():.1f}°C'),('Below 18°C*',f'{(df.temperature_c.lt(18).mean()*100):.1f}%'),('Days with data',f'{df.date.nunique()}')]
 cs=st.columns(4)
 for col,(label,val) in zip(cs,cards):col.metric(label,val)
 if source=='chart' and (start!=date(2026,10,1) or end!=date(2026,11,10)):st.caption('* Calculated from chart-digitised approximate points, not raw sensor measurements.')
 elif source=='uploaded':st.caption('* Calculated from the uploaded file.')

fig=go.Figure()
fig.add_hrect(y0=18,y1=20,fillcolor='rgba(89,223,208,.12)',line_width=0)
fig.add_hline(y=18,line=dict(color='rgba(89,223,208,.65)',dash='dot',width=1))
fig.add_hline(y=20,line=dict(color='rgba(89,223,208,.65)',dash='dot',width=1))
for label,color in [('Historical sensor series',SKY),('Post-23 October series',GOLD),('Uploaded sensor data',SKY)]:
 d=df[df.series==label]
 if d.empty:continue
 fig.add_trace(go.Scatter(x=d.date,y=d.temperature_c,mode='lines+markers',name=label,line=dict(color=color,width=3.3,shape='spline',smoothing=.65),marker=dict(size=5,color=color),hovertemplate='%{x|%d %b %Y}<br>%{y:.1f}°C<extra>'+label+'</extra>'))
# Weather series are real API values; absent on error.
for col,label,color in [('outside_c','London outdoor temperature',AQUA),('feels_like_c','London feels-like temperature','#c0a7ff')]:
 if col in merged and merged[col].notna().any():
  fig.add_trace(go.Scatter(x=merged.date,y=merged[col],name=label,mode='lines',line=dict(color=color,width=2.2,shape='spline',smoothing=.55,dash='dot'),hovertemplate='%{x|%d %b %Y}<br>%{y:.1f}°C<extra>'+label+'</extra>',visible=True if page=='London weather' else 'legendonly'))
fig.update_layout(height=460,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#bed0df',size=12),margin=dict(l=12,r=10,t=15,b=20),hovermode='x unified',legend=dict(orientation='h',y=-.2,x=0),xaxis=dict(showgrid=True,gridcolor='#243b51',title=''),yaxis=dict(showgrid=True,gridcolor='#243b51',title='Temperature (°C)'),uirevision='temperature')

if page=='Overview':
 st.subheader('Temperature & environmental context')
 st.plotly_chart(fig,use_container_width=True)
 l,r=st.columns([1.12,1])
 with l:
  st.subheader('Compliance breakdown')
  below_n=int(df.temperature_c.lt(18).sum())
  within_n=int(df.temperature_c.between(18,20,inclusive='both').sum())
  above_n=int(df.temperature_c.gt(20).sum())
  if source=='chart':
   st.caption('Distribution based on chart-reconstructed daily points; not the original sensor sample distribution.')
  else:
   st.caption('Distribution calculated from uploaded daily sensor averages.')
  donut=go.Figure(go.Pie(
      labels=['Below 18°C','Within 18–20°C','Above 20°C'],
      values=[below_n,within_n,above_n],hole=.68,
      marker=dict(colors=[GOLD,AQUA,'#f17b85'],line=dict(color=NAVY,width=3)),
      textinfo='percent',textfont=dict(size=13,color='#f0f7ff'),
      hovertemplate='%{label}: %{value} days (%{percent})<extra></extra>'
  ))
  donut.update_layout(height=335,paper_bgcolor='rgba(0,0,0,0)',
      font=dict(color='#e3effa'),margin=dict(l=0,r=0,t=10,b=5),
      legend=dict(orientation='h',y=-.08,x=.02,font=dict(size=11)),
      annotations=[dict(text=f'{len(df)}<br><span style="font-size:11px">days</span>',
          x=.5,y=.5,showarrow=False,font=dict(size=25,color='#fff'))])
  st.plotly_chart(donut,use_container_width=True)
 with r:
  st.subheader('Operational interpretation')
  st.markdown('**Target:** 18–20 °C. Blue represents the historical sensor series; amber represents the post-23 October continuation. Enable London weather in the trend chart legend to compare outdoor conditions.')
  st.subheader('Data reliability')
  st.markdown('**Reported KPIs** are transcribed from the supplied figure. **Daily points** are chart reconstructions until original sensor readings are provided. **London weather** comes from Open-Meteo.')
elif page=='Temperature trends':
 st.subheader('Daily evolution · smooth curve')
 st.plotly_chart(fig,use_container_width=True)
 st.caption('Spline smoothing affects the line drawing only; it does not create additional readings. Hover points to inspect the daily values.')
elif page=='London weather':
 st.subheader('Chiller vs London outdoor conditions')
 st.plotly_chart(fig,use_container_width=True)
 if not weather.empty:
  cs=st.columns(3);cs[0].metric('London average outdoor',f'{weather.outside_c.mean():.1f}°C');cs[1].metric('London average feels-like',f'{weather.feels_like_c.mean():.1f}°C');cs[2].metric('Weather days',len(weather))
 st.caption('Open-Meteo historical archive: hourly temperature_2m and apparent_temperature, aggregated to daily means in Europe/London time. These are gridded meteorological estimates, not direct warehouse sensor readings.')
else:
 st.subheader('Source and audit trail')
 st.markdown('**Chart-derived reconstruction:** approximate points transcribed from the supplied graphic, with two distinct series. **Reported summary:** 17.30°C mean, 15.8°C minimum, 80.5% below 18°C, as printed on the graphic. **Weather:** Open-Meteo archive API, central London coordinates, hourly data aggregated to daily averages. No missing values are fabricated.')
 st.markdown('**To replace approximations with verified measurements:** upload the original sensor CSV/XLSX using the collapsed Data controls panel. The uploaded file is processed during this session and is not written to the project repository by this app.')
 st.dataframe(merged,use_container_width=True,hide_index=True)
 st.download_button('Download combined dataset (CSV)',merged.to_csv(index=False).encode('utf-8'),'dincer_temperature_london_combined.csv',mime='text/csv')

if page!='Data & methodology':
 with st.expander('View and export source table'):
  st.dataframe(merged,use_container_width=True,hide_index=True)
  st.download_button('Export selected period (CSV)',merged.to_csv(index=False).encode('utf-8'),'dincer_temperature_london.csv',mime='text/csv')
st.markdown('<div style="border-top:1px solid #27435c;margin-top:30px;padding-top:14px;color:#8da7bc;font-size:.72rem">CASA LUKER INTELLIGENCE · DİNÇER Logistics · Source-aware analytics</div>',unsafe_allow_html=True)
