import pandas as pd
import plotly.express as px
import country_converter as coco

milk_production = pd.read_csv('production_milk_EU.csv')
cows = pd.read_csv('number_of_dairy_cows.csv')
pd.set_option('display.max_columns', None)

milk_production = milk_production[milk_production['dairyprod'].isin(['D1110A'])]

# drop columns
milk_production = milk_production.drop(columns=['DATAFLOW', 'LAST UPDATE', 'freq', 'dairyprod', 'milkitem', 'OBS_FLAG'])
milk_production = milk_production.rename(columns={'TIME_PERIOD': 'year', 'geo': 'country', 'OBS_VALUE': 'milk_production'})
cows = cows.drop(columns=['DATAFLOW', 'LAST UPDATE', 'freq', 'animals', 'month', 'unit', 'OBS_FLAG'])
cows = cows.rename(columns={'TIME_PERIOD': 'year', 'geo': 'country', 'OBS_VALUE': 'cows'})

# Check for duplicate values
print("Duplicates in milk_production:", milk_production.duplicated().sum())
print("Duplicates in cows:", cows.duplicated().sum())

# Merge the two dataframes
df = pd.merge(milk_production, cows, on=['country', 'year'])
df.head(20)

# filtering for maps
year = 2022
df['country'] = df['country'].replace('EL', 'GR') # Greece
country = coco.convert(names=df['country'], to="ISO3")
df['country_ISO3'] = country
mapdf = df.groupby(['milk_production', 'cows', 'country_ISO3', 'year']).size().reset_index()
mapdf = mapdf[mapdf['country_ISO3'] != 'not found'] # remove not found (total eu values)
filtered_mapdf = mapdf[mapdf['year'] == year]

# MELK PRODUCTIE
fig = px.choropleth(locations=filtered_mapdf['country_ISO3'], color=filtered_mapdf['milk_production'], scope='europe',
                    color_continuous_scale='RdYlGn', title=f'Milk production in Europe in {year}')
fig

# AANTAL KOE
fig = px.choropleth(locations=filtered_mapdf['country_ISO3'], color=filtered_mapdf['cows'], scope='europe',
                    color_continuous_scale='RdYlGn', title=f'Koe in Europa in {year}')
fig