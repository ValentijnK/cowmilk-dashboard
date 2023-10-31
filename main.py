import pandas as pd

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