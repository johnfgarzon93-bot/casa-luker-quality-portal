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
NAVY='#091525'; PANEL='#13273d'; AQUA='#59dfd0'; GOLD='#f1b94e'; SKY='#71aaf2'; MUTED='#ffffff'
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
[data-testid="stMetricLabel"]{color:#ffffff!important;font-size:.78rem!important;letter-spacing:.025em}
[data-testid="stMetricValue"]{font-size:clamp(1.35rem,2.4vw,2rem)!important;color:#fff!important;overflow-wrap:anywhere}
[data-testid="stVerticalBlockBorderWrapper"]>div{border-color:#28445e!important;border-radius:16px!important}
.stButton>button,.stDownloadButton>button{border-radius:12px;background:#183750;color:#e8f8ff;border:1px solid #38566c}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#59dfd0;color:#59dfd0}
[data-testid="stAlert"]{border-radius:14px!important;background:#17334a!important;border:1px solid #315570!important;color:#fff!important}
[data-testid="stAlert"] *,[data-testid="stAlert"] p,[data-testid="stAlert"] span{color:#fff!important;opacity:1!important}
[data-testid="stAlert"] svg{fill:none!important;color:#65dfd1!important}
/* Chart text is configured separately through Plotly layout. */
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}

/* Consistent white typography across Streamlit components */
.stApp, .stApp p, .stApp span, .stApp label, .stApp li,
.stApp h1, .stApp h2, .stApp h3, .stApp h4,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
[data-testid="stMetricLabel"] *, [data-testid="stMetricValue"] *,
[data-testid="stWidgetLabel"] *,
[data-testid="stRadio"] label, [data-testid="stRadio"] label *,
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary *,
[data-testid="stFileUploader"] label, [data-testid="stFileUploader"] small,
[data-testid="stDataFrame"] label {color:#ffffff!important;opacity:1!important}
.stApp input, .stApp textarea, .stApp select,
.stApp button, .stApp button *, .stApp [role="button"] {color:#ffffff!important}
.stApp input::placeholder, .stApp textarea::placeholder {color:#ffffff!important;opacity:.85!important}
.stApp [data-testid="stMetric"] {overflow:hidden}
.stApp [data-testid="stMetricValue"] {line-height:1.2!important}


/* Control panel: no white-on-white, including Streamlit BaseWeb inputs */
[data-testid="stExpander"] {background:#12283e!important;border:1px solid #35536c!important;border-radius:14px!important;overflow:hidden}
[data-testid="stExpander"] details, [data-testid="stExpander"] summary {background:#12283e!important;color:#fff!important}
[data-testid="stExpander"] summary:hover {background:#1c3951!important}
[data-testid="stExpander"] summary *, [data-testid="stExpander"] summary svg {color:#fff!important;fill:currentColor!important}
[data-testid="stFileUploaderDropzone"] {background:#1b344b!important;border:1px dashed #68869d!important;border-radius:12px!important}
[data-testid="stFileUploaderDropzone"] *,[data-testid="stFileUploaderDropzone"] small {color:#fff!important;opacity:1!important}
[data-testid="stFileUploaderDropzone"] button {background:#31516c!important;border:1px solid #86a5ba!important;color:#fff!important}
[data-testid="stDateInput"] [data-baseweb="input"], [data-testid="stDateInput"] input,
[data-testid="stDateInput"] [data-baseweb="base-input"],
[data-testid="stDateInput"] [data-baseweb="input"]>div {background:#1b344b!important;color:#fff!important;border-color:#68869d!important}
[data-testid="stDateInput"] input, [data-testid="stDateInput"] svg {color:#fff!important;fill:#fff!important;opacity:1!important}
[data-testid="stDateInput"] input::placeholder {color:#e6eef7!important}
[data-testid="stRadio"] label *, [data-testid="stRadio"] p {color:#fff!important;opacity:1!important}
[data-testid="stRadio"] [role="radiogroup"] {gap:1.1rem!important}
[data-testid="stRadio"] [role="radio"] {border-color:#d7e7f5!important}

@media(max-width:750px){.block-container{padding:1rem .85rem 2rem}[data-testid="stMetric"]{padding:12px}[data-testid="stMetricValue"]{font-size:1.35rem!important}}
</style>''',unsafe_allow_html=True)

st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;border-bottom:1px solid #28435a;padding:4px 0 18px"><div style="font-weight:800;letter-spacing:.11em;color:#f0f8ff;font-size:1rem"><img alt="Bandera de Colombia" title="Colombia" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDYwIDQwIj48cmVjdCB3aWR0aD0iNjAiIGhlaWdodD0iMjAiIGZpbGw9IiNGQ0QxMTYiLz48cmVjdCB5PSIyMCIgd2lkdGg9IjYwIiBoZWlnaHQ9IjEwIiBmaWxsPSIjMDAzODkzIi8+PHJlY3QgeT0iMzAiIHdpZHRoPSI2MCIgaGVpZ2h0PSIxMCIgZmlsbD0iI0NFMTEyNiIvPjwvc3ZnPg==" style="width:33px;height:22px;object-fit:cover;border-radius:3px;vertical-align:middle;margin-right:10px;box-shadow:0 0 0 1px #ffffff44"/> CASA LUKER <span style="color:#ffffff">INTELLIGENCE</span> <img alt="Bandera del Reino Unido" title="United Kingdom" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDYwIDQwIj48cmVjdCB3aWR0aD0iNjAiIGhlaWdodD0iNDAiIGZpbGw9IiMwMTIxNjkiLz48cGF0aCBkPSJNMCAwTDYwIDQwTTYwIDBMMCA0MCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSI5Ii8+PHBhdGggZD0iTTAgMEw2MCA0ME02MCAwTDAgNDAiIHN0cm9rZT0iI0M4MTAyRSIgc3Ryb2tlLXdpZHRoPSI0Ii8+PHBhdGggZD0iTTMwIDBWNDBNMCAyMEg2MCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIxMyIvPjxwYXRoIGQ9Ik0zMCAwVjQwTTAgMjBINjAiIHN0cm9rZT0iI0M4MTAyRSIgc3Ryb2tlLXdpZHRoPSI3Ii8+PC9zdmc+" style="width:33px;height:22px;object-fit:cover;border-radius:3px;vertical-align:middle;margin-left:10px;box-shadow:0 0 0 1px #ffffff44"/></div><div style="font-size:.76rem;color:#ffffff">COLOMBIA × UNITED KINGDOM · QUALITY OPERATIONS</div></div>',unsafe_allow_html=True)
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
with st.expander('⚙ Filters & data upload',expanded=False):
 a,b,c=st.columns([2,1,1]);uploaded=a.file_uploader('Upload sensor data (CSV / Excel)',type=['csv','xlsx']);start=b.date_input('From',value=date(2026,10,1),min_value=date(2026,10,1),max_value=date(2026,11,10));end=c.date_input('To',value=date(2026,11,10),min_value=date(2026,10,1),max_value=date(2026,11,10))
 st.caption('Weather: Central London · Outdoor conditions are shown for comparison only.')

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
st.title({'Overview':'Casa Luker | Executive Intelligence','Temperature trends':'Chiller temperature trends','London weather':'London weather intelligence','Data & methodology':'Data management & methodology'}[page])
st.caption(f'{start:%d %B} – {end:%d %B %Y}  ·  Target 18.0–20.0 °C  ·  {"Uploaded sensor file" if source=="uploaded" else "Chart-derived reconstruction"}')
if source=='chart':
 st.markdown('<div style="background:#17334a;border:1px solid #315570;border-left:4px solid #59dfd0;border-radius:12px;padding:13px 17px;color:#fff;font-size:.89rem;line-height:1.55"><b>REPORT SNAPSHOT</b> &nbsp; · &nbsp; Mean <b>17.30°C</b> &nbsp; · &nbsp; Minimum <b>15.8°C</b> &nbsp; · &nbsp; Below target <b>80.5%</b><div style="font-size:.78rem;color:#e6f1fa;margin-top:5px">Reported sensor KPIs · Daily trend reconstructed from supplied chart; exact daily sensor readings not available.</div></div>',unsafe_allow_html=True)
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
fig.update_layout(height=460,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#ffffff',size=13),margin=dict(l=12,r=10,t=15,b=20),hovermode='x unified',legend=dict(orientation='h',y=-.23,x=0,font=dict(color='#ffffff',size=12),bgcolor='rgba(0,0,0,0)',itemclick='toggle',itemdoubleclick='toggleothers'),xaxis=dict(showgrid=True,gridcolor='#243b51',title=''),yaxis=dict(showgrid=True,gridcolor='#243b51',title='Temperature (°C)'),uirevision='temperature')

if page=='Overview':
 st.markdown('<div style="font-size:.8rem;letter-spacing:.12em;color:#59dfd0;font-weight:750;margin:8px 0 12px">LONDON WEATHER × CHILLER PERFORMANCE</div>',unsafe_allow_html=True)
 if not weather.empty and weather['outside_c'].notna().any():
  w1,w2,w3=st.columns(3)
  w1.metric('London · outdoor mean',f"{weather['outside_c'].mean():.1f}°C")
  w2.metric('London · feels-like mean',f"{weather['feels_like_c'].mean():.1f}°C" if weather['feels_like_c'].notna().any() else 'N/A')
  w3.metric('London · available weather days',f"{weather['outside_c'].notna().sum()}")
 else:
  st.info('London weather data is unavailable for this period. The platform does not substitute estimated values.')
 st.subheader('London weather and chiller · daily evolution')
 for trace in fig.data:
  if trace.name in ('London outdoor temperature','London feels-like temperature'):
   trace.visible=True
 st.plotly_chart(fig,use_container_width=True)
 st.caption('Chiller: chart-based daily series or uploaded sensor file · London: Open-Meteo historical daily averages. Hover to compare dates.')
 st.subheader('Chiller compliance & London weather averages')
 left,right=st.columns(2,gap='large')
 def make_donut(labels,values,center,colors):
  donut=go.Figure(go.Pie(
   labels=labels,values=values,hole=.70,sort=False,
   marker=dict(colors=colors,line=dict(color=NAVY,width=4)),
   textinfo='percent',textfont=dict(color='#ffffff',size=14),
   hovertemplate='%{label}<br>%{value} days · %{percent}<extra></extra>'
  ))
  donut.update_layout(
   height=355,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
   font=dict(color='#ffffff',size=13),margin=dict(l=5,r=5,t=8,b=48),
   legend=dict(orientation='h',x=.5,xanchor='center',y=-.15,
               font=dict(color='#ffffff',size=12),bgcolor='rgba(0,0,0,0)'),
   annotations=[dict(text=center,x=.5,y=.5,showarrow=False,
                     font=dict(color='#ffffff',size=22))]
  )
  return donut
 with left:
  st.markdown('#### Chiller · target compliance')
  below_n=int(df.temperature_c.lt(18).sum())
  within_n=int(df.temperature_c.between(18,20,inclusive='both').sum())
  above_n=int(df.temperature_c.gt(20).sum())
  st.plotly_chart(make_donut(['Below 18°C','Within 18–20°C','Above 20°C'],
      [below_n,within_n,above_n],f"{len(df)}<br><span style='font-size:12px'>days</span>",
      [GOLD,AQUA,'#f17b85']),use_container_width=True)
  st.caption('Distribution of daily points in the selected chiller series; not the 80.5% reported sensor-reading KPI.')
 with right:
  st.markdown('#### London · weather averages')
  outdoor=weather['outside_c'].dropna() if 'outside_c' in weather.columns else pd.Series(dtype=float)
  apparent=weather['feels_like_c'].dropna() if 'feels_like_c' in weather.columns else pd.Series(dtype=float)
  if outdoor.empty or apparent.empty:
   st.info('London weather data is unavailable for the selected dates. No values have been substituted.')
  else:
   air_mean=outdoor.mean()
   feel_mean=apparent.mean()
   difference=feel_mean-air_mean
   st.markdown(f"""
   <div style="background:linear-gradient(130deg,#193c58 0%,#10253b 90%);border:1px solid #40647c;border-radius:22px;padding:28px 26px;min-height:350px;color:white;box-shadow:0 12px 28px #020d1a40">
    <div style="font-size:12px;letter-spacing:2px;font-weight:800;color:#72eadb">LONDON · AVERAGE WEATHER</div>
    <div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:25px">
     <div style="background:#224863;border:1px solid #54748b;border-radius:17px;padding:19px 15px">
      <div style="font-size:14px;color:#ffffff">🌡️ Air temperature</div>
      <div style="font-size:clamp(27px,3vw,48px);font-weight:800;color:#ffffff;letter-spacing:-2px;margin:16px 0 8px">{air_mean:.1f}°C</div>
      <div style="font-size:12px;color:#e3f3fa">Average outdoor</div>
     </div>
     <div style="background:#224863;border:1px solid #54748b;border-radius:17px;padding:19px 15px">
      <div style="font-size:14px;color:#ffffff">💨 Feels-like</div>
      <div style="font-size:clamp(27px,3vw,48px);font-weight:800;color:#ffffff;letter-spacing:-2px;margin:16px 0 8px">{feel_mean:.1f}°C</div>
      <div style="font-size:12px;color:#e3f3fa">Average apparent</div>
     </div>
    </div>
    <div style="border-top:1px solid #54748b;margin-top:24px;padding-top:16px;font-size:14px;color:#ffffff">Feels-like vs air: <b style="color:#72eadb">{difference:+.1f}°C</b> &nbsp; · &nbsp; {len(outdoor)} days of outdoor data</div>
   </div>""",unsafe_allow_html=True)
   st.caption('Central London · Open-Meteo hourly observations aggregated into daily averages for the selected period.')
 st.markdown('<div style="background:#132b40;border:1px solid #30506a;border-radius:14px;padding:15px 20px;color:#ffffff;line-height:1.55;font-size:.94rem"><b style="color:#59dfd0">EXECUTIVE TAKEAWAY</b> · Reported chiller mean: <b>17.30°C</b> against an <b>18–20°C</b> target; <b>80.5%</b> of the original reported readings were below 18°C. London weather is an external benchmark, not a chiller measurement.</div>',unsafe_allow_html=True)
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
st.markdown('<div style="border-top:1px solid #27435c;margin-top:30px;padding-top:14px;color:#ffffff;font-size:.72rem">CASA LUKER INTELLIGENCE · DİNÇER Logistics · Source-aware analytics</div>',unsafe_allow_html=True)
