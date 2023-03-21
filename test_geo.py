import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point

df = pd.read_csv('/Users/javierjaramillo/Desktop/chatbot/app/new_data.csv')
df = df[['lat', 'log']]
#print(df.columns)
#print(df.head())
#df = df.head(1000)
gdf = gpd.read_file('/Users/javierjaramillo/Desktop/chatbot/app/cb_2013_us_county_500k.geojson')
doc = {}
data_out = []

#filter geojson by LSAD 13
gdf = gdf[gdf['LSAD'] == '13']
geometry = [Point(xy) for xy in zip(df.log, df.lat)]  # create a shapely Point for each row in the DataFrame

def get_county_name(x):
    for idx, poly in enumerate(gdf.geometry):
        if x.within(poly):
            print('Name: ', gdf.iloc[idx]['Name'])
            return gdf.iloc[idx]['Name']
    print('None')
    return 'ZMunicipio'

#check if the point is in the polygon
for idx, p in enumerate(geometry):
    doc['lat'] = df.iloc[idx]['lat']
    doc['log'] = df.iloc[idx]['log']
    doc['county'] = get_county_name(p)
    data_out.append(doc)
    doc = {}
        
df1 = pd.DataFrame(data_out)
df1.to_csv('/Users/javierjaramillo/Desktop/chatbot/app/county.csv', encoding='utf-8', index=True)