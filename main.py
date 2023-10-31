import pandas as pd

milk_production = pd.read_csv('production_milk_EU.csv')
cows = pd.read_csv('number_of_dairy_cows.csv')
pd.set_option('display.max_columns', None)

milk_production = milk_production[milk_production['dairyprod'].isin(['D1110A'])]
milk_production = milk_production[milk_production['TIME_PERIOD'].isin([2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2021, 2022])]

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
df.head(25)