import csv,datetime
from pathlib import Path
# Visual chart reading: x-axis 1 Oct to 10 Nov, approximate ordinate values.
blue=[17.6,17.3,17.3,17.2,17.5,17.4,17.1,16.6,16.7,17.9,18.3,18.5,17.8,17.6,17.1,16.9,16.7,16.5,16.4,16.7,17.7,18.2,17.9]
yellow=[17.8,18.2,17.7,16.7,17.0,17.3,17.7,18.2,18.5,18.0,17.9,17.8,18.4,17.9,18.0,18.2,18.3,17.8]
assert len(blue)+len(yellow)==41
start=datetime.date(2026,10,1)
with open(Path(__file__).parent/'data'/'chart_reconstruction.csv','w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['date','temperature_c','series','source_quality'])
 for i,v in enumerate(blue+yellow):
  w.writerow([(start+datetime.timedelta(days=i)).isoformat(),v,'Historical sensor series' if i<23 else 'Post-23 October series','Approximate reading digitised from supplied chart image; not raw sensor export'])
